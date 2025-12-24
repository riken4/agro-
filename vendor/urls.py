
from django.urls import path,include


from . import views


urlpatterns = [
	path('', views.vendor_dashboard, name='vendor_dashboard_page'),

	# Products
	path('products/', views.vendor_products_all, name='vendor_products_all'),
	path('products/available/', views.vendor_products_available, name='vendor_products_available'),
	path('products/in-transit/', views.vendor_products_in_transit, name='vendor_products_in_transit'),
	path('products/<int:pk>/', views.vendor_product_detail, name='vendor_product_detail'),

	# Warehouse
	path('warehouse/', views.vendor_browse_warehouse, name='vendor_browse_warehouse'),
	path('warehouse/<int:pk>/', views.vendor_warehouse_detail, name='vendor_warehouse_detail'),

	# Orders
	path('orders/', views.vendor_orders_all, name='vendor_orders_all'),
	path('orders/pending/', views.vendor_orders_pending, name='vendor_orders_pending'),
	path('orders/processing/', views.vendor_orders_processing, name='vendor_orders_processing'),
	path('orders/shipped/', views.vendor_orders_shipped, name='vendor_orders_shipped'),
	path('orders/delivered/', views.vendor_orders_delivered, name='vendor_orders_delivered'),
	path('orders/<int:order_id>/', views.vendor_order_detail, name='vendor_order_detail'),

	# Finance
	path('finance/wallet/', views.vendor_finance_wallet, name='vendor_finance_wallet'),
	path('finance/payouts/', views.vendor_finance_payouts, name='vendor_finance_payouts'),
	path('finance/earnings/', views.vendor_finance_earnings, name='vendor_finance_earnings'),

	# Utility pages
	path('reviews/', views.vendor_reviews, name='vendor_reviews'),
	path('notifications/', views.vendor_notifications, name='vendor_notifications'),
	path('settings/shop/', views.vendor_shop_settings, name='vendor_shop_settings'),
	path('profile/', views.vendor_profile, name='vendor_profile'),
]

