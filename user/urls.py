from django.urls import path
from . import views

app_name = "user"

urlpatterns = [
    path('login/', views.loginPageView, name='login'),
    path('register/', views.registerPageView, name='register'),
    path('account/<int:id>/', views.accountPageView, name='account'),
    path('logout/', views.logoutUser, name='logout'),
]