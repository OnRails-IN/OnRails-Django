from django.urls import path
from . import views

urlpatterns = [
	path('login/', views.LoginHandler),
	path('signup/', views.SignupHandler),
	path('all/', views.ListUsernamesHandler),
	path('achievements/', views.UserAchievementsHandler)
]