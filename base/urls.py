from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('dashboard/', views.dashboard, name='dashboard'),
]