from django.urls import path
from . import views
from . import views_temp

app_name = 'services'

urlpatterns = [
    # ONLY the home page for now
    path('', views.home, name='home'),
    path('temp-create-admin/', views_temp.temp_create_admin, name='temp_create_admin'),
]

