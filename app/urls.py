from django.urls import path
from . import views

app_name = "app"

urlpatterns = [
    path('', views.homePageView, name='homepage'),
    path('order/<int:id>/', views.orderView, name='order'),
]