from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # ONLY the home page for now
    path('', views.home, name='home'),
]
