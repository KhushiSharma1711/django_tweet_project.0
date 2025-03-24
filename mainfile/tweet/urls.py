from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('tweet/<int:pk>/', views.tweet_detail, name='tweet_detail'),
    path('tweet/new/', views.tweet_new, name='tweet_create'),
    path('tweet/<int:pk>/edit/', views.tweet_edit, name='tweet_edit'),
    path('tweet/<int:pk>/delete/', views.tweet_delete, name='tweet_delete'),
    path('tweet/<int:pk>/like/', views.like_tweet, name='like_tweet'),
    path('tweet/<int:pk>/dislike/', views.dislike_tweet, name='dislike_tweet'),
    path('tweet/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('tweet/<int:pk>/comments/', views.get_comments, name='get_comments'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html', next_page='tweet_list'), name='logout'),
]

