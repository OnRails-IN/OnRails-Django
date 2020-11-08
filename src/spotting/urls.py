from django.urls import path
from . import views

urlpatterns = [
	path('new/', views.NewSpottingHandler),
	path('list/', views.ListSpottingHandler),
	path('user/', views.UserSpottingHandler),
	path('edit/', views.EditSpottingHandler),
	path('search/', views.SearchSpottingHandler)
]