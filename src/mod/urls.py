from django.urls import path
from . import views

urlpatterns = [
	path('create/database/', views.CreateDBHandler),
	path('create/document/', views.CreateDocHandler),
	path('truncate/', views.TruncateDBHandler),
	path('health/', views.HealthHandler),
	path('update/', views.UpdateDBHandler)
]