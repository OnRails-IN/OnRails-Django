from django.urls import path
from . import views

urlpatterns = [
	path('new/', views.NewJourneyHandler),
	path('list/', views.UserJourneysHandler),
	path('list/time/', views.TimeJourneysHandler),
	path('edit/', views.EditJourneyHandler),
	path('search/', views.SearchJourneysHandler)
]