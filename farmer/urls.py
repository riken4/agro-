
from django.urls import path,include


from . import views


urlpatterns = [
    
    path('',views.farmer_dashboard,name='farmer_dashboard_page'),
 
    path('products/', views.farmer_products_all, name='farmer_products_all'),
	path('products/<int:product_id/', views.farmer_product_detail, name='farmer_product_detail'),
    path('product/add',views.farmer_add_product,name="farmer_product_add"),
    path('product/edit/<int:product_id>/',views.farmer_edit_product,name='farmer_product_edit'),
    path('product/delete/<int:product_id>/',views.farmer_product_delete,name='farmer_product_delete'),
    path('products/pending/', views.farmer_pending_products, name='farmer_pending_products'),
    path('products/selected/', views.farmer_selected_products, name='farmer_selected_products'),
    path('products/<int:product_id>/vendor-selections/', views.farmer_selected_products_detail,name='farmer_vendor_selections_detail'),
    path('product/delivered/',views.farmer_delivered_products,name='farmer_deliverd_products'),\

]
 
    


