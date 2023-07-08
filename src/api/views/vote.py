from datetime import datetime
import uuid
from rest_framework import generics
from rest_framework import viewsets,views,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from ..serializers import QuestionDetailPageSerializer,VoteCommentSerializer
from ..models import Vote,VoteComment,Choice,Profile,User
from ..pagenations.vote_pagenation import LargeResultsSetPagination
from rest_framework.response import Response 
from .user import UserAPIView
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Q
from .token_vertify import TokenVertify

class VoteAPIView(views.APIView,LimitOffsetPagination):
  permission_classes = [AllowAny,]


  def get(self,request):
      print("投稿を取得します")
      JWT = request.COOKIES.get("access_token")
      if "type" in request.GET:
        query = request.GET.get("type")
        print("type",query)

        
        if query == "me":
          # vote/?type=me
          # 自分の投稿を取得する

          userid = UserAPIView.get_object(self,JWT)
          user = Profile.objects.get(user=userid)
          vote = Vote.objects.filter(user=user).order_by('-createdAt')
          serializer = QuestionDetailPageSerializer(vote, many=True)

          return Response(serializer.data,status=status.HTTP_201_CREATED)
        elif query == "voted":
          # 自分が投票したやつを取得する
          userid = UserAPIView.get_object(self,JWT)
          vote = Vote.objects.filter(numberOfVotes=userid).order_by('-createdAt')
          serializer = QuestionDetailPageSerializer(vote, many=True)
          return Response(serializer.data,status=status.HTTP_201_CREATED)   
        elif query == "unvoted":
          # 自分が投票してないやつを取得する
          userid = UserAPIView.get_object(self,JWT)
          vote = Vote.objects.filter(~Q(numberOfVotes=userid),isLimitedRelease=False).order_by('-createdAt')[0:5]
          serializer = QuestionDetailPageSerializer(vote, many=True)
          return Response(serializer.data,status=status.HTTP_201_CREATED) 
    
        else:
          # 自分以外のuserの投稿を取得する時に使うやつ
          user_id = request.data["user_id"]
          vote = Vote.objects.filter(user=user_id,isLimitedRelease=False)
          serializer = QuestionDetailPageSerializer(vote, many=True)
          return Response(serializer.data,status=status.HTTP_201_CREATED) 
      elif "q" in request.GET:
        
        query = request.GET.get("q")
        print(query,"で検索")
        vote = Vote.objects.filter(Q(questionText__contains =query),isLimitedRelease=False).order_by('-createdAt')
        serializer = QuestionDetailPageSerializer(vote, many=True)
        return Response(serializer.data,status=status.HTTP_201_CREATED)

      else:
        # 全て取得
        # ここをページネーションにしたい
        JWT = request.COOKIES.get("access_token")
        # access_tokenがなければ取得させない
        
        # resultがcomplete以外であれば認証に失敗している
        
        print("検証が完了")
        queryset = Vote.objects.filter(isLimitedRelease=False).order_by('-createdAt')
        results = self.paginate_queryset(queryset,request,view=self)
        serializer = QuestionDetailPageSerializer(results, many=True)
        
        return self.get_paginated_response(serializer.data)
      return 

  

      

 
  def post(self,request): 
    JWT = request.COOKIES.get("access_token")
    if JWT == None:
      pass
    result = TokenVertify.vertify(request,JWT)
    if result == "complete":
      user = UserAPIView.get_object(self,JWT)
      print("投稿を保存します",self.request.user)
      user = Profile.objects.get(user=user)
      vote_id = str(uuid.uuid4())
    
      
      Vote.objects.create(id=vote_id,user=user,questionText=request.data["questionText"],isLimitedRelease=request.data["isLimitedRelease"])

      #Voteを作った後に選択肢を作成する
      vote_instance = Vote.objects.get(id=vote_id) 
      choices = request.data["choices"]
      for choice in choices:
        choice_data = {"text":choice["text"],"vote":vote_instance}
        print(choice_data)
        Choice.objects.create(**choice_data)
      
      vote = Vote.objects.filter(pk=vote_id)
      serializer = QuestionDetailPageSerializer(vote, many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response(result,status=status.HTTP_401_UNAUTHORIZED)
    
from django.contrib.auth import logout

class VoteDetailAPIView(views.APIView):
  permission_classes = [AllowAny,]

  def get(self,request,pk):
    print("詳細データを取得します")
    vote = Vote.objects.filter(pk=pk)
    serializer = QuestionDetailPageSerializer(vote, many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)


  def put(self, request, pk):
    print("投票します")
    # 未ログインuserが投票する
    isAnonymous = False
    print(self.request.data)
    userid = self.request.data["userid"]
    
    
    # アカウントがないuser
    if userid == "":
      user = User.objects.create()
      user.save()
      isAnonymous = True
    else:
      user = User.objects.get(pk=userid)


  
    #pkからvoteを取得する
    print(user,"が投票します")
    vote_id = pk
    vote_data = Vote.objects.get(id=vote_id) 
  
     #voteのnumberOfVotesにuserを追加する
      
    print(user,"が投票しました")
    vote_data.numberOfVotes.add(user)
    vote_data.save()
      

    choiceID = request.data["choiceID"]
    choice_data = Choice.objects.get(id=choiceID)
    choice_data.votedUserCount.add(user)
    choice_data.save()

      # アノニマスであればuseridを返す
    if isAnonymous:
      return Response({"userid":user.pk})

    return Response({"message":"PUTしました"})
  

  def delete(self, request, pk):
    print("削除します。")
    vote = Vote.objects.get(id=pk) 
    vote.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)



#Voteに対するコメント
class CommentVoteAPIView(views.APIView):
  permission_classes = [AllowAny,]
  def get(self,request,pk):
    print(pk,"のvoteのコメントを取得する")

    comment = VoteComment.objects.order_by('-createdAt').filter(vote=pk)
    serializer = VoteCommentSerializer(comment,many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)
  

  def post(self,request,pk):
    
    print(pk,"のvoteにコメントを追加する")
    request_data = self.request.data 
    now = datetime.now()
    date = '{:%Y-%m-%d %H:%M}'.format(now) 
    vote_instance =  Vote.objects.get(pk=pk)
    # 認証する
    JWT = request.COOKIES.get("access_token")
    if JWT == None:
      pass
    print("jwt",JWT)
    result = TokenVertify.vertify(request,JWT)

    if result == "complete":
      userid = UserAPIView.get_object(self,JWT)
    else:
      print("認証が通らなかった")

    profile_instance = Profile.objects.get(user=userid)
    id = uuid.uuid4() 
    request_data.update(
        {
          "id":id,
          "createdAt": date,
          "vote":vote_instance,
          "user":profile_instance,
        }
      )
    data = VoteComment.objects.create(**request_data)
    
    comment = VoteComment.objects.order_by('-createdAt').filter(vote=pk)
    serializer = VoteCommentSerializer(comment,many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)
    
  def delete(self,requset,pk):
    pass

