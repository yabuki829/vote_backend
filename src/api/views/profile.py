


from rest_framework import viewsets,views,status
from rest_framework.permissions import AllowAny
from ..serializers import ProfileSerializer, QuestionDetailPageSerializer
from ..models import  User,Vote,Profile
from rest_framework.response import Response 
from .user import UserAPIView
from .token_vertify import TokenVertify


class ProfileViewSets(viewsets.ModelViewSet):
  queryset = Profile.objects.all()
  serializer_class = ProfileSerializer

  def perform_create(self, serializer):
    if Profile.objects.filter(user=self.request.user).exists() == False:
      serializer.save(user=self.request.user)




#Profileの詳細　
class ProfileDetailAPIView(views.APIView):
  def get(self,request,pk):
    if "type" in request.GET:
     
      query = request.GET.get("type")
      if query == "vote":
        # 投稿を取得する
        user = Profile.objects.get(user=pk)
        vote = Vote.objects.filter(user=user).order_by('-createdAt')
        serializer = QuestionDetailPageSerializer(vote,many=True)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    else: 
      profile = Profile.objects.filter(user=pk)
      serializer = ProfileSerializer(profile, many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)






# 自分のプロフィール
class ProfileAPIView(views.APIView):
  
  #一覧ではなく自分のprofileを取得する
  permission_classes = [AllowAny,]
  def get(self,request):
    # accesstokenからuseridを取得する
    print("プロフィールを取得します")
    JWT = request.COOKIES.get("access_token")
    if JWT == None:
      return
    result = TokenVertify.vertify(request,JWT)
    if result == "complete":

      userid = UserAPIView.get_object(self,JWT)
      profile = Profile.objects.filter(user=userid)
      serializer = ProfileSerializer(profile, many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response(result,status=status.HTTP_401_UNAUTHORIZED)
  def post(self,request):

    Profile.objects.create(user=self.request.user)
    profile = Profile.objects.filter(user=self.request.user)
    serializer = ProfileSerializer(profile, many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)

  # Profileの変更の際に使う
  def put(self,request):
    JWT = request.COOKIES.get("access_token")
    if JWT == None:
      return Response(result,status=status.HTTP_401_UNAUTHORIZED)
      
    result = TokenVertify.vertify(request,JWT)

    if result == "complete":
      userid = UserAPIView.get_object(self,JWT)
      user_profile = Profile.objects.get(user=userid)
      print(self.request.data)
      if "type" in request.GET:
        print("画像以外を変更します")
        query = request.GET.get("type")
        if query == "none":
          user_profile.nickName = self.request.data["nickName"]
          user_profile.bio = self.request.data["bio"]
          user_profile.save()
        
      else:
        print("画像も変更します")
        user_profile.nickName = self.request.data["nickName"]
        user_profile.image = self.request.data["profileImage"]
        user_profile.bio = self.request.data["bio"]
        user_profile.save()

      profile = Profile.objects.filter(user=userid)
      serializer = ProfileSerializer(profile, many=True)
      return Response(serializer.data,status=status.HTTP_201_CREATED)

    return Response(result,status=status.HTTP_401_UNAUTHORIZED)
  




 #自分以外のユーザーのプロフィール
class OtherProfileAPIView(views.APIView):
  def get(self,request,pk):
    user = User.objects.get(pk=pk)
    profile = Profile.objects.get(user=user)
    serializer = ProfileSerializer(profile, many=True)
    return Response(serializer.data,status=status.HTTP_201_CREATED)

