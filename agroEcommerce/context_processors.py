from .models import Organization, Order, Vendor, Farmer, VendorPayoutRequest, FarmerPayoutRequest, Notification


def organization_context_processor(request):
    organization = Organization.objects.first()
    return {
        'organization': organization
    }


def total_orders_payout_requests_context_processor(request):
    
    total_orders = 0
    total_pending_orders=0
    total_vendor_payout_requests = 0
    total_farmer_payout_requests = 0
    total_farmer_kyc_pending=0
    total_vendor_kyc_pending=0
    if not request.user.is_authenticated:
        return {
            'total_orders': total_orders,}
    if request.user.role.role == 'admin':
        total_farmer_kyc_pending = Farmer.objects.filter(verification_status='pending').count()
        total_vendor_kyc_pending = Vendor.objects.filter(verification_status='pending').count()
        total_orders = Order.objects.exclude(status='delivered').count()
        total_pending_orders = Order.objects.filter(status='pending').count()
        total_vendor_payout_requests = VendorPayoutRequest.objects.filter(status='pending').count()
        total_farmer_payout_requests = FarmerPayoutRequest.objects.filter(status='pending').count()
    elif request.user.role.role == 'vendor':
        total_pending_orders = Order.objects.filter(status='pending', items__vendor_product__vendor=request.user.vendor).distinct().count()
        total_orders = Order.objects.filter(items__vendor_product__vendor=request.user.vendor, status__in=['pending', 'processing', 'shipped']).distinct().count()
        total_vendor_payout_requests = VendorPayoutRequest.objects.filter(vendor=request.user.vendor, status='pending').count()
    elif request.user.role.role == 'farmer':
        total_pending_orders = Order.objects.filter(status='pending', items__vendor_product__farmer_product__farmer=request.user.farmer).distinct().count()
        total_orders = Order.objects.filter(items__vendor_product__farmer_product__farmer=request.user.farmer, status__in=['pending', 'shipped']).distinct().count()
        total_farmer_payout_requests = FarmerPayoutRequest.objects.filter(farmer=request.user.farmer, status='pending').count()
    return {
        
        'total_orders': total_orders,
        'total_farmer_kyc_pending':total_farmer_kyc_pending,
        'total_vendor_kyc_pending':total_vendor_kyc_pending,
        'total_pending_orders':total_pending_orders,
        'total_vendor_payout_requests': total_vendor_payout_requests,
        'total_farmer_payout_requests': total_farmer_payout_requests,
    }


def notifications_context_processor(request):
    notifications = []
    if not request.user.is_authenticated:
        return  {'notifications_list': notifications}
    
    if request.user.role.role == 'admin':
        notifications = Notification.objects.filter(is_read=False).order_by('-created_at')[:8]
        
    elif request.user.role.role == 'vendor':
        notifications=Notification.objects.filter(is_read=False,user=request.user).order_by('-created_at')[:8]
    
    elif request.user.role.role == 'farmer':
        notifications=Notification.objects.filter(is_read=False,user=request.user).order_by('-created_at')[:8]

    return {
        'notifications_list': notifications,

    }
