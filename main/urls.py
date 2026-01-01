from django.urls import path
from . import views

urlpatterns = [
        path('', views.home, name='home'), 
        path('', views.home1, name='home1'),
        path('about/', views.about, name='about'), 
        path('contact/', views.contact, name='contact'), 
        path('farmers/', views.farmers, name='farmers'), 
        path('products/', views.products, name='products'), 
        path('products_detail/', views.products_detail, name='products_detail'), 
        path('vendor/', views.vendor, name='vendor'), 
        path('cart/', views.cart, name='cart'), 
        path('vender_detail/', views.vender_detail, name='vender_detail'), 

]