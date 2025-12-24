
from django.urls import path,include


from . import views


urlpatterns = [
    
    path('',views.farmer_dashboard,name='farmer_dashboard_page'),
 
    
    
]

