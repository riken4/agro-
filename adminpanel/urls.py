
from django.urls import path,include


from . import views


urlpatterns = [
    path('',views.admin_dashboard,name='admin_dashboard_page'),
    
    # Orders
    path('orders/',views.order_list,name='admin_order_list_page'),
    path('order/pending/',views.order_pending_list,name='admin_order_pending_page'),
    path('order/delivered/',views.order_delivered_list,name='admin_order_delivered_page'),
    path('order-details/<int:order_id>/',views.order_details,name='admin_order_details'),
    
    
    # Farmer
    path('farmers/',views.farmer_list,name='admin_farmer_list_page'),
    path('farmer/edit/<int:farmer_id>/',views.farmer_edit,name='admin_farmer_edit_page'),
    path('farmer/delete/<int:farmer_id>/',views.farmer_delete,name='admin_farmer_delete'),
    path('farmer/products/<int:farmer_id>/',views.farmer_product_list,name='admin_farmer_products_list'),
    path('farmer-details/<int:farmer_id>/',views.farmer_details,name='admin_farmer_details_page'),
    
    path('farmer-kyc-pending/',views.farmer_kyc_pending,name='admin_farmer_kyc_pending_page'),
    path('farmer/payout-requests/',views.farmer_payout_requests,name='admin_farmer_payout_requests_page'),
    
    path('api/farmer-payment-payout-status-change/',views.FarmerPaymentPayoutStatusChangeAPIView.as_view(),name='admin_farmer_payout_status_change_api' ),
    path('api/farmer-kyc-status-change/',views.FarmerKYCChangeAPIView.as_view(),name='admin_farmer_kyc_change_api' ),
    
    
    # Vendor
    path('vendor/',views.vendor_list,name='admin_vendor_list_page'),
    path('vendor-details/<int:vendor_id>/',views.vendor_details,name='admin_vendor_details_page'),
    path('vendor/edit/<int:vendor_id>/',views.vendor_edit,name='admin_vendor_edit_page'),
    path('vendor/delete/<int:vendor_id>/',views.vendor_delete,name='admin_vendor_delete'),
    path('vendor/products/<int:vendor_id>/',views.vendor_product_list,name='admin_vendor_products_list'),
    
    path('vendor-kyc-pending/',views.vendor_kyc_pending,name='admin_vendor_kyc_pending_page'),
    path('vendor/payout-requests/',views.vendor_payout_requests,name='admin_vendor_payout_requests_page'),
    
    path('api/vendor-kyc-status-change/',views.VendorKYCChangeAPIView.as_view(),name='admin_vendor_kyc_change_api'),
    path('api/vendor-payment-payout-status-change/',views.VendorPaymentPayoutStatusChangeAPIView.as_view(),name='admin_vendor_payout_status_change_api' ),
    
    
    # Products
    path('all-farmer/products/',views.all_farmer_product_list,name='admin_all_farmer_product_list_page'),
    path('all-vendor/products/',views.all_vendor_product_list,name='admin_all_vendor_product_list_page'),
    path('categories/',views.category_list,name='admin_category_list_page'),
    path('category/add/',views.category_add,name='admin_category_add_page'),
    path('category/edit/<int:category_id>/',views.category_edit,name='admin_category_edit_page'),
    path('category/delete/<int:category_id>/',views.category_delete,name='admin_category_delete'),
    
    # Custumer Management
    path('customers/',views.customer_list,name='admin_customer_list_page'),
    path('customer/delete/<int:customer_id>/',views.customer_delete,name='admin_customer_delete'),
    
    
    # Reviews and Ratings
    path('reviews/',views.review_list,name='admin_review_list_page'),
    path('review/delete/<int:review_id>/',views.review_delete,name='admin_review_delete'),
    
    # Admin Wallet & Commission
    path('finance/',views.admin_wallet,name='admin_wallet_page'),
    path('finance/order-detail/<int:order_id>/',views.order_income_detail,name='admin_order_income_detail'),
    path('finance/revenue-report/', views.revenue_report, name='admin_revenue_report_page'),
    path('finance/commission-rate/',views.commission_rate,name='admin_commission_rate_page'),
    path('finance/commission-rate/edit/',views.commission_rate_edit,name='admin_commission_rate_edit_page'),
    
    # Notifications
    path('notifications/',views.notification_list,name='admin_notification_list_page'),
    
    # Activity Logs
    path('activity-logs/',views.activity_logs_list,name='admin_activity_logs_page'),
    
    # Organization
    path('organization/',views.organization_view,name='admin_organization_page'),
    path('organization/edit/',views.organization_edit,name='admin_organization_edit_page'),
    path('change-password/',views.change_password,name='admin_change_password_page'),
    
    
    
 
    
    
]

