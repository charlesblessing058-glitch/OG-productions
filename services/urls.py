from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),
    path('logout/', views.client_logout, name='logout'),
]
