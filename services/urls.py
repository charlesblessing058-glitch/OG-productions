from django.urls import path
from . import views
from . import views_temp

app_name = 'services'

urlpatterns = [
    # ONLY the home page for now
    path('', views.home, name='home'),
    path('temp-create-admin/', views_temp.temp_create_admin, name='temp_create_admin'),
    # Authentication
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),
    path('logout/', views.client_logout, name='logout'),
]


