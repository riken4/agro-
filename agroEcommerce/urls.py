"""
URL configuration for agroEcommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('login/',views.login_page,name='login_page'),
    path('logout/',views.logout_page,name='logout'),
    path('admin-dashboard/',include('adminpanel.urls')),
    path('vendor-dashboard/',include('vendor.urls')),
    path('farmer-dashboard/',include('farmer.urls')),
    
      path('', views.home, name='home'), 
        path('about/', views.about, name='about'), 
        path('contact/', views.contact, name='contact'), 
        path('farmers/', views.farmers, name='farmers'), 
        path('products/', views.products, name='products'), 
        path('products_detail/', views.products_detail, name='products_detail'), 
        path('vendor/', views.vendor, name='vendor'), 
        path('cart/', views.cart, name='cart'), 
        path('vendor_detail/', views.vendor_detail, name='vendor_detail'), 
        path('checkout/', views.checkout, name='checkout'), 
        path('vegetables/', views.vegetables, name='vegetables'), 
        path('farmers_detail/', views.farmers_detail, name='farmers_detail'), 
        path('order_confirmation/', views.order_confirmation, name='order_confirmation'), 
        path('privacy_policy/', views.privacy_policy, name='privacy_policy'), 
        path('faq/', views.faq, name='faq'),
        path('term_of_services/', views.term_of_services, name='term_of_services'),
        path('refund_and_return/', views.refund_and_return, name='refund_and_return'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)