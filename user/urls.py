from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPageView, name='login'),
    path('register/', views.registerPageView, name='register'),
]