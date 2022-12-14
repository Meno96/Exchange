from django.urls import path
from . import views

urlpatterns = [
    path('', views.homePageView, name='homePage'),
    path('order', views.orderView, name='order'),
]