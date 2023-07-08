

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager,PermissionsMixin
from django.conf import settings
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError("Email is must")
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=20,default="質問")    
    def __str__(self):
      return self.title

class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    email = models.EmailField(max_length=100, unique=True,null=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    # 20000829　のような形で年齢を記憶している
    dateOfBirth = models.IntegerField(default=0) 
    # 性別
    # 0 -> 未選択
    # 1 -> 男性
    # 2 -> 女性
    gender = models.IntegerField(default=0)
    # 最後にいつtokenのやりとりをしたか
    # 最後にアクセストークンを取得したり更新したりしたか
    lastAccess = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "email"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], condition=models.Q(email__isnull=False), name='unique_email')
        ]

    def __str__(self):
        return str(self.id)

    def user_id(self):
        return self.id.__str__()


def upload_profile_image_path(instance, filename):
    #jpg png などの拡張子の部分を取得する
    ext = filename.split('.')[-1]
    return '/'.join(['images/profiles',str(uuid.uuid4())+str(".")+str(ext)])

def upload_post_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['images/posts', str(uuid.uuid4())+str(".")+str(ext)])

class Profile(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
  nickName = models.CharField(max_length=20,default="No Name")
  user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name="user",on_delete=models.CASCADE)
  createdAt = models.DateTimeField(auto_now_add=True) 
  bio = models.CharField(max_length=120,default="はじめまして")
  image = models.ImageField(blank=True, null=True, upload_to=upload_profile_image_path)
  def __str__(self):
      return self.nickName




class Vote(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    questionText = models.CharField(max_length=200)
    createdAt = models.DateTimeField(auto_now_add=True) 
    image = models.ImageField(blank=True, null=True, upload_to=upload_profile_image_path)
    #urlを知っている人のみ投票ができる
    isLimitedRelease = models.BooleanField(default=False)
    numberOfVotes = models.ManyToManyField(User, blank=True,related_name="numberOfVotes")
    tags = models.ManyToManyField(Tag)
    def __str__(self) -> str:
       return self.questionText




class Choice(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    text = models.CharField(max_length=200)
    #誰がこの選択肢に投票したのか
    votedUserCount = models.ManyToManyField(User, blank=True)
    vote = models.ForeignKey(Vote,blank=True,on_delete=models.CASCADE,related_name="choices") 
    def __str__(self) -> str:
       return self.text


  

class Thread(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  vote = models.ForeignKey(Vote, blank=True, on_delete=models.CASCADE )
  title = models.CharField(max_length=100)
  createdAt = models.DateTimeField(auto_now_add=True) 
  def __str__(self) -> str:
       return self.title


class ThreadComment(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
  text = models.CharField(max_length=100)
  createdAt = models.DateTimeField(auto_now_add=True) 
  

  def __str__(self) -> str:
       return self.text



class VoteComment(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
  user = models.ForeignKey(Profile, on_delete=models.CASCADE)
  vote = models.ForeignKey(Vote, on_delete=models.CASCADE)
  text = models.CharField(max_length=100)
  createdAt = models.DateTimeField(auto_now_add=True) 
  def __str__(self) -> str:
       return  self.text