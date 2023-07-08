from rest_framework import generics,views,status
from rest_framework.permissions import AllowAny,IsAuthenticated
from ..serializers import UserSerializer
from ..models import User,Profile

from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response 
from django.conf import settings
# ipアドレスを取得する
def get_client_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[0]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip

# 仮会員登録する
class CreateUserView(generics.CreateAPIView):
  serializer_class = UserSerializer
  permission_classes = [AllowAny,]

  def perform_create(self, serializer):
    return super().perform_create(serializer)

# 本登録を完了させる
class UserActivateView(views.APIView):
  permission_classes = [AllowAny,]

  def check_activate_token(self,uidb64,token):
    try:
      uid = urlsafe_base64_decode(uidb64).decode()
      user = User.objects.get(pk=uid)
    except Exception as e:
      print("例外:", e)
      return False
    
    if default_token_generator.check_token(user,token):
      user.is_active = True
      user.save()
      return True
    else:
      print("セーブできませんでした")
    return False

  def post(self,request):
    # 暗号化したトークンを検証する
    # 認証に成功したら
    # profileを作成する
    
    uidb64 = request.data["uidb64"]
    token = request.data["token"]
    # 認証 uidとトークン 
    if self.check_activate_token(uidb64,token):
      print("")
      #  profileを作成する
      user_id = urlsafe_base64_decode(uidb64).decode()
      user = User.objects.get(pk=user_id)
      profile = Profile.objects.create(user=user)
      profile.save()
      data = {
        "message":"成功しました"
      }
      return Response(data,status=status.HTTP_201_CREATED)
    else:
      # 認証に失敗しました。
      data = {
        "message":"失敗しました"
      }
      return Response(data,status=status.HTTP_201_CREATED)
      


from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework_simplejwt import views as jwt_views
from rest_framework_simplejwt import exceptions as jwt_exp
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
)
# トークンをリフレッシュする
class TokenRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny,]
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
      print("リフレッシュ")

      refresh = self.request.COOKIES.get("refresh_token")
      if refresh:
            try:
              access = RefreshToken(refresh)
              res = Response({"message":"complete"}, status=status.HTTP_200_OK)
              print("新しいアクセストークンを設定します")
              res.set_cookie(
                  "access_token",
                  access,
                  max_age=60 * 60 * 24,
                  httponly=True,
                  secure=True,
                  path='/',
                  samesite="None"
                )

              return res
            except Exception as e:
                print("エラー",e)
                res = Response({"error":"refresh token is invalid"}, status=status.HTTP_401_UNAUTHORIZED)
                # cookieのrefreshtokenを削除する
                return res
      print("ここ呼ばれてる")
      res = Response({"error":"No Refresh Token"}, status=status.HTTP_401_UNAUTHORIZED)
      return res

# ログイン部分
class TokenObtainView(TokenObtainPairView):
  permission_classes = [AllowAny,]
  def post(self, request, *args, **kwargs):
    print("ログインします")
    serializer = self.get_serializer(data=request.data)
    try:
      print("ok1")
      serializer.is_valid(raise_exception=True)
    except jwt_exp.TokenError as e:
      print("ok2")
      raise jwt_exp.InvalidToken(e.args[0])

    res = Response(serializer.validated_data, status=status.HTTP_200_OK)
    try:
      res.delete_cookie("access_token")
    except Exception as e:
      print("エラー",e)

    print("ok3")
    res.delete_cookie("access_token")
    res.delete_cookie("refresh_token")

    res.set_cookie(
	    "access_token",
	    serializer.validated_data["access"],
	    max_age=60 * 60 * 24,
	    httponly=True,
      secure=True,
      path='/',
      samesite="None"
	  )
    res.set_cookie(
      "refresh_token",
      serializer.validated_data["refresh"],
      max_age=60 * 60 * 24 * 30,
      httponly=True,
      secure=True,
      path='/',
      samesite="None"
    
    )
    res.set_cookie("test","test",path='/',httponly=False,samesite="None",secure=False)
    res.set_cookie("islog","true",path='/',samesite="None")
    return res

  

import jwt

class UserAPIView(views.APIView):
    permission_classes = [AllowAny,]
    # 他のviewClassから参照されてる
    def get_object(self, JWT):
        try:
            payload = jwt.decode(
                jwt=JWT, key=settings.SECRET_KEY, algorithms=["HS256"]
            )
            return User.objects.get(id=payload["user_id"])

        except jwt.ExpiredSignatureError:
	    # access tokenの期限切れ
            return "Activations link expired"
        except jwt.exceptions.DecodeError:
            return "Invalid Token"
        except User.DoesNotExist:
            return "user does not exists"

    def get(self, request):
        
        JWT = request.COOKIES.get("access_token")
        
        print("JWTToken",JWT)
        if not JWT:
            return Response(
                {"error": "No token"}, status=status.HTTP_400_BAD_REQUEST
            )
        user = self.get_object(JWT)
        print("結果",user)
        if type(user) == str:
            return Response(
                {"error": user}, status=status.HTTP_400_BAD_REQUEST
            )

        if user.is_active:
            serializer = UserSerializer(user)
            return Response(serializer.data)
        return Response(
            {"error": "user is not active"}, status=status.HTTP_400_BAD_REQUEST
        )


class LogoutAPIView(views.APIView):
  permission_classes = [AllowAny,]
  def post(self,request, *args, **kwargs):
    # access と refresh のトークンを削除する
    
    print(self.request.COOKIES.get("test"))
    
    res = Response({"message":"complete"}, status=status.HTTP_200_OK)
    # cookieの削除の方法がわからんかったから内容をNoneに変更して期限を短くした。
    res.set_cookie(
	    "access_token",
	    "None",
	    max_age=1,
	    httponly=True,
      secure=True,
      path='/',
      samesite="None"
	  )
    res.set_cookie(
      "refresh_token",
      "None",
      max_age=1,
      httponly=True,
      secure=True,
      path='/',
      samesite="None"
    
    )
    return res

