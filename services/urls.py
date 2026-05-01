from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # ONLY the home page - guaranteed to work
    path('', views.home, name='home'),
]