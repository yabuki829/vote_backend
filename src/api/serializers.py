from datetime import timezone
from urllib.request import Request
from django.http import HttpResponse
from rest_framework.decorators import action
from rest_framework import serializers
from .models import  User,Vote,VoteComment,Thread,ThreadComment,Choice,Profile,Tag
from django.contrib.auth import get_user_model


from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.conf import settings
from django.core.mail import send_mail

# メールの本文
subject = "登録確認"
message_temp  = """
ご登録ありがとうございます。
以下のURLから登録を完了してください。
""" 




def create_activate_email(user):
    # uidをエンコードする
    
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = f'https://localhost:3000/activate/{uid}/{token}'
    message = f'Please activate your account by clicking the link below:\n\n{activation_url}'
    # subject : 送信するメールの件名を指定する必要があります。
    # message: 送信するメールの本文を指定する必要があります。
    # from_email: メールを送信するアドレスを指定する必要があります。
    # recipient_list: 送信先のメールアドレスを指定する必要があります。リスト形式で指定します。
    # fail_silently: 送信に失敗した場合に例外を発生させずに、Falseを指定することができます。Trueに設定すると、失敗しても例外を発生させません。
    send_mail(
        subject,
        message,
        "syodai829@icloud.com",
        [user.email],
        fail_silently=False,
    )

class UserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ["id", "email","password","gender","dateOfBirth",]
    extra_kwargs= {'password': {'write_only': True},'email': {'write_only': True}}



  def create(self ,validated_data,commit=True):
    user = get_user_model().objects.create_user(email=validated_data["email"],password=validated_data["password"])
    # メールを確認するまでログインをさせない
    user.is_active = False
    user.gender = validated_data["gender"]
    user.dateOfBirth = validated_data["dateOfBirth"]
    print("作成")
    if commit :
      user.save()
      # メールを送信する
      create_activate_email(user)
    return user 
  
  

class ProfileSerializer(serializers.ModelSerializer):
  user = UserSerializer(read_only=True)
  class Meta:
    model = Profile
    fields = ["id","nickName","user","createdAt","image","bio"]
    extra_kwargs = {'user': {'read_only': True}}

 
class ChoiceSerializer(serializers.ModelSerializer):
  votedUserCount = UserSerializer(read_only=True,many=True)
  id = serializers.UUIDField(read_only=True)
  text = serializers.CharField(max_length=200)

  class Meta:
    model = Choice
    fields = ["id","text","votedUserCount"]
    extra_kwargs = {'user': {'read_only': True}}
  
  def create(self, validated_data):
      print("Choiceを作成します")
      return Choice.objects.create(**validated_data)



class TagSerializer(serializers.ModelSerializer):
  class Meta:
    model = Tag
    fields = ["id","title"]


class VoteSerializer(serializers.ModelSerializer):
  createdAt = serializers.DateTimeField(format="%Y年%m月%d日", read_only=True)
  user = ProfileSerializer(read_only=True)
  choices = ChoiceSerializer()
  numberOfVotes = UserSerializer(read_only=True,many=True)
  tags = TagSerializer(many=True)
  class Meta:
    model = Vote
    fields = ["id","user","questionText","createdAt","image","isLimitedRelease","choices","numberOfVotes","tags"]
    extra_kwargs = {'user': {'read_only': True}}
  

  def create(self, validated_data):
    return Vote.objects.create(**validated_data)
    
class ChoiceSerializerWithVotes(ChoiceSerializer):
    votes = serializers.UUIDField(read_only=True)

class QuestionDetailPageSerializer(VoteSerializer):
  choices = ChoiceSerializer(many=True, read_only=True)
  
class QuestionResultPageSerializer(VoteSerializer):
  choices = ChoiceSerializerWithVotes(many=True, read_only=True)

  


#TODO スレッド　コメントのシリアライザーを作成する

class VoteThreadSerializer(serializers.ModelSerializer):
  createdAt = serializers.DateTimeField(format="%Y年%m月%d日", read_only=True)
  user = ProfileSerializer(read_only=True)
  choices = ChoiceSerializer(read_only=True,many=True)
  numberOfVotes = UserSerializer(read_only=True,many=True)
  class Meta:
    model = Vote
    fields = ["id","user","questionText","createdAt","image","isLimitedRelease","choices","numberOfVotes"]
    extra_kwargs = {'user': {'read_only': True}}



class ThreadSerializer(serializers.ModelSerializer):
  createdAt = serializers.DateTimeField(format="%Y年%m月%d日", read_only=True)
  vote = VoteThreadSerializer()
  user = ProfileSerializer(read_only=True)
  class Meta:
    model = Thread
    fields = ["id","user","vote","title","createdAt"]
    extra_kwargs = {'user': {'read_only': True}}

class ThreadCommentSerializer(serializers.ModelSerializer):
  createdAt = serializers.DateTimeField(format="%Y年%m月%d日", read_only=True)
  user = ProfileSerializer()
  class Meta:
    model = ThreadComment
    fields = ["id","user","text","createdAt"]


class VoteCommentSerializer(serializers.ModelSerializer):
  createdAt = serializers.DateTimeField(format="%Y年%m月%d日%H:%M", read_only=True)
  user = ProfileSerializer()
  class Meta:
    model = VoteComment
    fields = "__all__"


