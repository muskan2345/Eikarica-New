from django.urls import path

from . import views

urlpatterns = [
    path('', views.cart_detail, name='cart'),
    path('success/<order>)', views.success, name='success'),
    path('payment/', views.payment, name='payment'),
]