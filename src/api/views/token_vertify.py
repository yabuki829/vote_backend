import jwt
from django.conf import settings
from ..models import User

class TokenVertify():
  def vertify(request,token):
    """JWTのトークンを検証する。正常であればcompleteという文字列を返す。正常でなければ{"error":" 内容"}の形でエラー内容を返す"""
    JWT = request.COOKIES.get("access_token")
    if not JWT:
        return  {"error": "No token"}
        
      # トークンを検証する
    try:
      payload = jwt.decode(jwt=JWT, key=settings.SECRET_KEY, algorithms=["HS256"])

      return "complete"       

    except jwt.ExpiredSignatureError:
	      # access tokenの期限切れ
        print("トークンの期限切れです")
        return  {"error": "Activations link expire"}
    except jwt.exceptions.DecodeError:
        print("無効なトークンです")
        return {"error": "Invalid Token"}
    except User.DoesNotExist:
        print("userが存在しません")
        return  {"error": "user does not exists"}
    
