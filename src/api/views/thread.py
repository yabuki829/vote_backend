from rest_framework import views,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from ..serializers import  ThreadCommentSerializer, ThreadSerializer
from ..models import Thread,ThreadComment,Profile,Vote
from rest_framework.response import Response 
from .user import UserAPIView
from .token_vertify import TokenVertify


#スレッドの詳細を取得する
class ThreadDetail(views.APIView):
  
  def get(self,request,pk):
    print("スレッドの詳細を取得します")
    JWT = request.COOKIES.get("access_token")

    if JWT == None:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

    result = TokenVertify.vertify(request,JWT)
    if result == "complete":
      thread = Thread.objects.filter(pk=pk)
      serializer = ThreadSerializer(thread, many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_401_UNAUTHORIZED)


class ThreadAPIView(views.APIView):
  
  def get(self,request):
    print("スレッド一覧を取得します。")
    thread = Thread.objects.all().order_by('-createdAt')
    serializer = ThreadSerializer(thread,many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)

  def post(self,request):
    
    JWT = request.COOKIES.get("access_token")
    if JWT == None:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

    result = TokenVertify.vertify(request,JWT)

    if result == "complete":
      userid = UserAPIView.get_object(self,JWT)
      user = Profile.objects.get(user=userid)
      vote = Vote.objects.get(pk=self.request.data["voteid"])
      Thread.objects.create(user=user,vote=vote,title=self.request.data["title"])

      thread = Thread.objects.all()
      serializer = ThreadSerializer(thread,many=True)

      return Response(serializer.data,status=status.HTTP_201_CREATED)
    
    return Response(status=status.HTTP_401_UNAUTHORIZED)

    


# 投稿のidから投稿に対するスレッドを取得する
class ThreadVoteAPIView(views.APIView):
    def get(self,request,pk):
      thread = Thread.objects.order_by('-createdAt').filter(vote=pk)
      serializer = ThreadSerializer(thread,many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)





#スレッドに対するコメント
class CommentThreadPIView(views.APIView):

  def get(self,request,pk):
    print("スレッドのコメントを取得します")
    JWT = request.COOKIES.get("access_token")

    if JWT == None:
      Response(status=status.HTTP_401_UNAUTHORIZED)
    result = TokenVertify.vertify(request,JWT)

    if result == "complete": 
      comment = ThreadComment.objects.filter(thread=pk)
      serializer = ThreadCommentSerializer(comment,many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_401_UNAUTHORIZED)
   

  def post(self,request,pk):  
    JWT = request.COOKIES.get("access_token")

    if JWT == None:
      return Response(status=status.HTTP_401_UNAUTHORIZED)

    result = TokenVertify.vertify(request,JWT)

    if result == "complete":
      userid = UserAPIView.get_object(self,JWT)
      print(userid)
      thread = Thread.objects.get(pk=pk)
      user = Profile.objects.get(user=userid)
      ThreadComment.objects.create(thread=thread,text=self.request.data["text"],user=user)
      
      comment = ThreadComment.objects.filter(thread=pk)
      serializer = ThreadCommentSerializer(comment,many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response("error",status=status.HTTP_401_UNAUTHORIZED)
 

