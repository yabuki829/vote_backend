from django.urls import path,include
from .views import vote,thread,profile,user,csrf
app_name = 'user'

urlpatterns = [
  path('register/', user.CreateUserView.as_view(), name='register'),
  path("encode/",user.UserActivateView.as_view()),

  path("activate/", user.UserActivateView.as_view(), name="activate"),

  path("vote/",vote.VoteAPIView.as_view(),name="vote"),
  path("vote/<str:pk>/comment/",vote.CommentVoteAPIView.as_view(),name="commentVote"),
  path("vote/<str:pk>/thread/",thread.ThreadVoteAPIView.as_view(),name="commentThread"),
  path("vote/<str:pk>/",vote.VoteDetailAPIView.as_view(),name="voteDetail"),
  
  
  
  
  path("thread/",thread.ThreadAPIView.as_view(),name="thread"),
  path("thread/<str:pk>/comment/",thread.CommentThreadPIView.as_view(),name="commentThread"),
  path("thread/<str:pk>/",thread.ThreadDetail.as_view(),name="voteDetail"),
  
  path("profile/",profile.ProfileAPIView.as_view(),name="profile"),
  path("profile/<str:pk>",profile.ProfileDetailAPIView.as_view(),name="profile"),
  

  path("user/",user.UserAPIView.as_view()),
  path("token/refresh/",user.TokenRefreshAPIView.as_view()),
  path("token/",user.TokenObtainView.as_view()),
  
  path('csrf/create',csrf.csrf),
  path("logout/",user.LogoutAPIView.as_view())
]
