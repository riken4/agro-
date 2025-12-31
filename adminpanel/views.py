from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,Avg
from django.utils import timezone
import calendar
from datetime import date


from datetime import timedelta
from decimal import Decimal
from agroEcommerce.models import (
    Order, Farmer, Vendor, FarmerProduct, VendorProduct, 
    Category, AdminWallet, FarmerPayoutRequest, VendorPayoutRequest,
    AuditLog, UserRole,Review,CommissionRate,Organization
)
from agroEcommerce.decorators import admin_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


# ========================
#  Dashboard Page
# ========================


@admin_required
def admin_dashboard(request):
    # Check if user is admin
    if not hasattr(request.user, 'role') or request.user.role.role != 'admin':
        return render(request, '403.html')
    
    # Date ranges
    today = timezone.now().date()
    last_month = today - timedelta(days=30)
    this_month_start = today.replace(day=1)
    
    # Total Revenue (from delivered and paid orders)
    total_revenue = Order.objects.filter(
        status='delivered',
        payment_status='paid'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # Revenue comparison with last month
    last_month_revenue = Order.objects.filter(
        status='delivered',
        payment_status='paid',
        delivered_at__gte=last_month,
        delivered_at__lt=this_month_start
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    this_month_revenue = Order.objects.filter(
        status='delivered',
        payment_status='paid',
        delivered_at__gte=this_month_start
    ).aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    if last_month_revenue > 0:
        revenue_change = ((this_month_revenue - last_month_revenue) / last_month_revenue * 100)
    else:
        revenue_change = 100 if this_month_revenue > 0 else 0
    
    # Total Orders
    total_orders = Order.objects.count()
    last_month_orders = Order.objects.filter(
        created_at__gte=last_month,
        created_at__lt=this_month_start
    ).count()
    this_month_orders = Order.objects.filter(
        created_at__gte=this_month_start
    ).count()
    
    if last_month_orders > 0:
        orders_change = ((this_month_orders - last_month_orders) / last_month_orders * 100)
    else:
        orders_change = 100 if this_month_orders > 0 else 0
    
    # Active Farmers
    active_farmers = Farmer.objects.filter(
        is_active=True,
        verification_status='verified',
     
    ).count()
    
    new_farmers_this_month = Farmer.objects.filter(
        is_active=True,
        created_at__gte=this_month_start,
        verification_status='verified'
    ).count()
    
    # Active Vendors
    active_vendors = Vendor.objects.filter(
        verification_status='verified',
        is_active=True
    ).count()
    
    new_vendors_this_month = Vendor.objects.filter(
        is_active=True,
        created_at__gte=this_month_start,
        verification_status='verified'
    ).count()
    
    # Recent Orders (last 5)
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    
    # Pending Payout Requests
    farmer_payout_requests = FarmerPayoutRequest.objects.filter(
        status='pending'
    ).select_related('farmer')[:3]
    
    vendor_payout_requests = VendorPayoutRequest.objects.filter(
        status='pending'
    ).select_related('vendor')[:3]
    
    # Pending Verifications
    pending_farmers = Farmer.objects.filter(
        is_active=True,
        verification_status='pending'
    ).count()
    
    pending_vendors = Vendor.objects.filter(
        is_active=True,
        verification_status='pending'
    ).count()
    
    # Admin Wallet
    admin_wallet = AdminWallet.objects.first()
    if not admin_wallet:
        admin_wallet = AdminWallet.objects.create()
    
    # Commission breakdown (approximate half-half)
    farmer_commission = admin_wallet.balance / 2
    vendor_commission = admin_wallet.balance / 2
    
    # Recent commission this month
    recent_commission = Order.objects.filter(
        status='delivered',
        payment_status='paid',
        delivered_at__gte=this_month_start
    ).count() * Decimal('10.00')  # Approximate
    
    # Product Counts
    farmer_products = FarmerProduct.objects.count()
    vendor_products = VendorProduct.objects.count()
    
    # Customer Count
    total_customers = UserRole.objects.filter(role='customer').count()
    
    # Categories
    total_categories = Category.objects.count()
    
    # Recent Audit Logs (last 6)
    recent_logs = AuditLog.objects.select_related('user').order_by('-created_at')[:6]
    
    context = {
        # Stats
        'total_revenue': total_revenue,
        'revenue_change': revenue_change,
        'total_orders': total_orders,
        'orders_change': orders_change,
        'active_farmers': active_farmers,
        'new_farmers_this_month': new_farmers_this_month,
        'active_vendors': active_vendors,
        'new_vendors_this_month': new_vendors_this_month,
        
        # Recent Orders
        'recent_orders': recent_orders,
        
        # Payout Requests
        'farmer_payout_requests': farmer_payout_requests,
        'vendor_payout_requests': vendor_payout_requests,
        
        # Verifications
        'pending_farmers': pending_farmers,
        'pending_vendors': pending_vendors,
        
        # Admin Wallet
        'admin_wallet': admin_wallet,
        'farmer_commission': farmer_commission,
        'vendor_commission': vendor_commission,
        'recent_commission': recent_commission,
        
        # Product & Customer Stats
        'farmer_products': farmer_products,
        'vendor_products': vendor_products,
        'total_customers': total_customers,
        'total_categories': total_categories,
        
        # Audit Logs
        'recent_logs': recent_logs,
    }
    
    return render(request, 'admin_pages/admin_dashboard.html', context)


# =========================
#  Order
# =========================
@admin_required
def order_list(request):
    order=Order.objects.all().order_by('-created_at','updated_at')
    total_pending_order=Order.objects.filter(status='pending').count()
    total_delivered_order=Order.objects.filter(status='delivered').count()
    return render(request,'admin_pages/order/order_list.html',{'orders':order,'total_pending_order':total_pending_order,'total_delivered_order':total_delivered_order})

@admin_required
def order_pending_list(request):
    order=Order.objects.filter(status='pending')
    total_orders=order.count()
    return render(request,'admin_pages/order/order_pending.html',{'orders':order,'total_orders':total_orders})


@admin_required
def order_delivered_list(request):
    order=Order.objects.filter(status='delivered')
    total_orders=order.count()
    return render(request,'admin_pages/order/order_delivered.html',{'orders':order,'total_orders':total_orders})


@admin_required
def order_details(request,order_id):
    order=Order.objects.get(id=order_id)
    return render(request,'admin_pages/order/order_detail.html',{'order':order})


# =========================
#  Farmer
# =========================

@admin_required
def farmer_list(request):
    farmers = Farmer.objects.filter(is_active=True).order_by('-created_at')
    total_farmers = farmers.count()
    total_pending = Farmer.objects.filter(is_active=True,verification_status='pending').count()
    total_verified = Farmer.objects.filter(is_active=True,verification_status='verified').count()
    total_rejected = Farmer.objects.filter(is_active=True,verification_status='rejected').count()
    
    context = {
        'farmers': farmers,
        'total_farmers': total_farmers,
        'total_pending': total_pending,
        'total_verified': total_verified,
        'total_rejected': total_rejected
    }
    
    return render(request, 'admin_pages/farmer/farmer_list.html', context)


@login_required
def farmer_edit(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    if request.method == 'POST':
        try:
            # Update User information
            user = farmer.user
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = request.POST.get('email')
            user.username = request.POST.get('username')
            user.save()
            
            # Update Farmer information
            farmer.farm_name = request.POST.get('farm_name')
            farmer.phone = request.POST.get('phone')
            farmer.description = request.POST.get('description', '')
            
            # Location
            farmer.province = request.POST.get('province')
            farmer.city = request.POST.get('city')
            farmer.address = request.POST.get('address')
            
            # KYC
            farmer.pan_number = request.POST.get('pan_number')
            farmer.citizenship_number = request.POST.get('citizenship_number', '')
            
            # Handle file uploads
            if request.FILES.get('pan_document'):
                farmer.pan_document = request.FILES['pan_document']
            
            if request.FILES.get('qr_image'):
                farmer.qr_image = request.FILES['qr_image']
            
            if request.FILES.get('citizenship_front'):
                farmer.citizenship_front = request.FILES['citizenship_front']
            
            if request.FILES.get('citizenship_back'):
                farmer.citizenship_back = request.FILES['citizenship_back']
            
            # Status
            old_verification_status = farmer.verification_status
            farmer.verification_status = request.POST.get('verification_status')
            farmer.is_active = request.POST.get('is_active') == '1'
            farmer.rejection_reason = request.POST.get('rejection_reason', '')
            
            # Update verified_at if status changed to verified
            if old_verification_status != 'verified' and farmer.verification_status == 'verified':
                farmer.verified_at = timezone.now()
            farmer.save()
            messages.success(request, f'Farmer "{farmer.farm_name}" updated successfully!')
            return redirect('admin_farmer_details', farmer_id=farmer.id)
        except Exception as e:
            messages.error(request, f'Error updating farmer: {str(e)}')
    context = {
        'farmer': farmer
    }
    return render(request, 'admin_pages/farmer/farmer_edit.html', context)

@admin_required
def farmer_delete(request,farmer_id):
    farmer=Farmer.objects.get(id=farmer_id)
    if farmer.objects.filter(farmer=farmer,delivery_status__in=['pending','selected','in_transit']).exists():
        messages.error(request,f"Cannot delete this farmer . There are active products ")
        return redirect('admin_farmer_list_page')
    farmer.is_active=False
    messages.success(request,'Farmer deleted successfully')
    return redirect('admin_farmer_list_page')


@admin_required
def farmer_product_list(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    products = FarmerProduct.objects.filter(farmer=farmer).order_by('-created_at')
    
    # Add aggregates for summary cards
    aggregates = products.aggregate(
        total_quantity=Sum('quantity'),
        avg_price=Avg('base_price')
    )
    total_stock=FarmerProduct.objects.filter(farmer=farmer).aggregate(total=Sum('available_quantity'))['total'] or 0
    
    context = {
        'farmer': farmer,
        'products': products,
        'aggregates': aggregates,
        'total_stock':total_stock
    }
    return render(request, 'admin_pages/farmer/farmer_products.html', context)


@admin_required 
def farmer_details(request,farmer_id):
    farmer=Farmer.objects.get(id=farmer_id)
    total_pending_payout_requests=FarmerPayoutRequest.objects.filter(farmer=farmer,status='pending').count()
    total_paid_payout_requests=FarmerPayoutRequest.objects.filter(farmer=farmer,status='paid').count()

    total_available_products=FarmerProduct.objects.filter(farmer=farmer,delivery_status='pending').count()
    total_products=FarmerProduct.objects.filter(farmer=farmer).count()
   
    return render(request,'admin_pages/farmer/farmer_detail.html',{'farmer':farmer,'total_products':total_products,'total_available_products':total_available_products,'total_pending_payout_requests':total_pending_payout_requests,'total_paid_payout_requests':total_paid_payout_requests})

@admin_required
def farmer_kyc_pending(request):
    farmers=Farmer.objects.filter(is_active=True,verification_status='pending').order_by('-created_at')
    total_kyc_pending=farmers.count()
    return render(request,'admin_pages/farmer/farmer_kyc_pending.html',{'farmers':farmers,'total_kyc_pending':total_kyc_pending})

@admin_required
def farmer_payout_requests(request):
    FarmerPayoutRequests = FarmerPayoutRequest.objects.filter(status='pending').select_related('farmer').order_by('-created_at')
    total_requests = FarmerPayoutRequests.count()
    total_peding_amount = FarmerPayoutRequests.aggregate(total=Sum('requested_amount'))['total'] or Decimal('0.00')
    total_approved_requests = FarmerPayoutRequest.objects.filter(status='paid').count()
    total_rejected_requests = FarmerPayoutRequest.objects.filter(status='rejected').count()
    context={
        'payout_requests': FarmerPayoutRequests,
        'total_requests': total_requests,
        'total_peding_amount': total_peding_amount,
        'total_approved_requests': total_approved_requests,
        'total_rejected_requests': total_rejected_requests,
    }
    return render(request, 'admin_pages/farmer/farmer_payout_requests.html', context)


class FarmerPaymentPayoutStatusChangeAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        payout_id = request.data.get('payout_id')
        new_status = request.data.get('new_status')
        admin_response = request.data.get('admin_response', '')

        try:
            payout_request = FarmerPayoutRequest.objects.get(id=payout_id)
            payout_request.status = new_status
            if new_status == 'rejected':
                payout_request.admin_response = admin_response
                
            if new_status == 'paid':
                payout_request.paid_at = timezone.now()
                # Deduct from Farmer Wallet
                farmer_wallet = payout_request.farmer.farmer_wallet
                if farmer_wallet.balance >= payout_request.amount:
                    farmer_wallet.balance -= payout_request.amount
                    farmer_wallet.save()
                else:
                    return Response({'error': 'Insufficient balance in farmer wallet'}, status=400)
            payout_request.save()
            return Response({'success': True, 'new_status': new_status})
        except FarmerPayoutRequest.DoesNotExist:
            return Response({'error': 'Payout request not found'}, status=404)
        
        

class FarmerKYCChangeAPIView(APIView): 
    permission_classes=[IsAdminUser]
    
    def post(self, request):
        farmer_id = request.data.get('farmer_id')
        new_status = request.data.get('new_status')
        reason= request.data.get('reason', '')

        try:
            farmer = Farmer.objects.get(id=farmer_id)
            farmer.verification_status = new_status
            farmer.verified_at = timezone.now() if new_status == 'verified' else None
            if new_status == 'rejected':
                farmer.rejection_reason = reason
          
            
            farmer.save()
            return Response({'success': True, 'new_status': new_status})
        except Farmer.DoesNotExist:
            return Response({'error': 'Farmer not found'}, status=404)



# ==============================
#  Vendors
# ==============================

@admin_required
def vendor_list(request):
    vendors=Vendor.objects.filter(is_active=True).order_by('-created_at')
    total_farmers = vendors.count()
    total_pending = Vendor.objects.filter(is_active=True,verification_status='pending').count()
    total_verified = Vendor.objects.filter(is_active=True,verification_status='verified').count()
    total_rejected = Vendor.objects.filter(is_active=True,verification_status='rejected').count()
    context={
        'vendors':vendors,
        'total_farmers':total_farmers,
        'total_pending':total_pending,
        'total_verified':total_verified,
        'total_rejected':total_rejected
    }
    
    return render(request,'admin_pages/vendor/vendor_list.html',context)

@admin_required
def vendor_edit(request,vendor_id):
    vendor=Vendor.objects.get(id=vendor_id)
    if request.method=='POST':
        try:
            # Update User information
            user=vendor.user
            user.first_name=request.POST.get('first_name')
            user.last_name=request.POST.get('last_name')
            user.email=request.POST.get('email')
            user.save()
            # Update Vendor information
            vendor.shop_name=request.POST.get('shop_name')
            vendor.phone=request.POST.get('phone')
            vendor.description=request.POST.get('description','')
            # Location
            vendor.province=request.POST.get('province')
            vendor.city=request.POST.get('city')
            vendor.address=request.POST.get('address')
            # KYC
            vendor.pan_number=request.POST.get('pan_number')

            # Handle file uploads
            if request.FILES.get('pan_document'):
                vendor.pan_document=request.FILES['pan_document']
                
            # Status
            old_verification_status=vendor.verification_status
            vendor.verification_status=request.POST.get('verification_status')
            #  qr
            if request.FILES.get('qr_image'):
                vendor.qr_image=request.FILES['qr_image']
                
            vendor.is_active=request.POST.get('is_active')=='1'
            vendor.rejection_reason=request.POST.get('rejection_reason','')
            # Update verified_at if status changed to verified
            if old_verification_status != 'verified' and vendor.verification_status == 'verified':
                vendor.verified_at = timezone.now()
            vendor.save()
            messages.success(request,f'Vendor "{vendor.shop_name}" updated successfully!')
            return redirect('admin_vendor_details_page',vendor_id=vendor.id)
        except Exception as e:
            messages.error(request,f'Error updating vendor: {str(e)}')
    
    return render(request,'admin_pages/vendor/vendor_edit.html',{'vendor':vendor})


@admin_required
def vendor_details(request,vendor_id):
    vendor=Vendor.objects.get(id=vendor_id)
    total_pending_payout_requests=VendorPayoutRequest.objects.filter(vendor=vendor,status='pending').count()
    total_paid_payout_requests=VendorPayoutRequest.objects.filter(vendor=vendor,status='paid').count()

    total_available_products=VendorProduct.objects.filter(vendor=vendor,delivery_status='pending').count()
    total_products=VendorProduct.objects.filter(vendor=vendor).count()
   
    return render(request,'admin_pages/vendor/vendor_detail.html',{'vendor':vendor,'total_products':total_products,'total_available_products':total_available_products,'total_pending_payout_requests':total_pending_payout_requests,'total_paid_payout_requests':total_paid_payout_requests})


@admin_required
def vendor_delete(request,vendor_id):
    vendor=Vendor.objects.get(id=vendor_id)
    if vendor.objects.filter(vendor=vendor,delivery_status__in=['pending','selected','in_transit']).exists():
        messages.error(request,f"Cannot delete this vendor . There are active products ")
        return redirect('admin_vendor_list_page')
    vendor.is_active=False
    messages.success(request,'Vendor deleted successfully')
    return redirect('admin_vendor_list_page')


@admin_required
def vendor_product_list(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    products = VendorProduct.objects.filter(vendor=vendor).order_by('-selected_at')
    
    # Add aggregates for summary cards
    aggregates = products.aggregate(
        total_quantity=Sum('selected_quantity'),
        avg_price=Avg('selling_price')
    )
    
    context = {
        'vendor': vendor,
        'products': products,
        'aggregates': aggregates,
    }
    return render(request, 'admin_pages/vendor/vendor_products.html', context)


@admin_required
def vendor_kyc_pending(request):
    vendors=Vendor.objects.filter(is_active=True,verification_status='pending').order_by('-created_at')
    total_kyc_pending=vendors.count()
    return render(request,'admin_pages/vendor/vendor_kyc_pending.html',{'vendors':vendors,'total_kyc_pending':total_kyc_pending})


@admin_required
def vendor_payout_requests(request):
    vendor_payout_requests = VendorPayoutRequest.objects.filter(status='pending').select_related('vendor').order_by('-created_at')
    total_requests = vendor_payout_requests.count()
    total_peding_amount = vendor_payout_requests.aggregate(total=Sum('requested_amount'))['total'] or Decimal('0.00')
    total_approved_requests = VendorPayoutRequest.objects.filter(status='paid').count()
    total_rejected_requests = VendorPayoutRequest.objects.filter(status='rejected').count()
    context={
        'payout_requests': vendor_payout_requests,
        'total_requests': total_requests,
        'total_peding_amount': total_peding_amount,
        'total_approved_requests': total_approved_requests,
        'total_rejected_requests': total_rejected_requests,
    }
    return render(request, 'admin_pages/vendor/vendor_payout_requests.html', context)



class VendorKYCChangeAPIView(APIView):
    permission_classes= [IsAdminUser]
    
    def post(self,request):
        vendor_id=request.data.get('vendor_id')
        new_status=request.data.get('new_status')
        reason=request.data.get('reason','')
        try:
            vendor=Vendor.objects.get(id=vendor_id)
            vendor.verification_status=new_status
            if new_status == 'verified':
                vendor.verified_at=timezone.now()
            if new_status == 'rejected':
                vendor.rejection_reason=reason
            vendor.save()
            return Response({'success':True,'new_status':new_status})

        except Vendor.DoesNotExist:
            return Response({'error':'Vendor not found'},status=404)

class VendorPaymentPayoutStatusChangeAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        payout_id = request.data.get('payout_id')
        new_status = request.data.get('new_status')
        admin_response = request.data.get('admin_response', '')

        try:
            payout_request = VendorPayoutRequest.objects.get(id=payout_id)
            payout_request.status = new_status
            if new_status == 'rejected':
                payout_request.admin_response = admin_response
                
            if new_status == 'paid':
                payout_request.paid_at = timezone.now()
                # Deduct from Vendor Wallet
                vendor_wallet = payout_request.vendor.vendor_wallet
                if vendor_wallet.balance >= payout_request.amount:
                    vendor_wallet.balance -= payout_request.amount
                    vendor_wallet.save()
                else:
                    return Response({'error': 'Insufficient balance in vendor wallet'}, status=400)
            payout_request.save()
            return Response({'success': True, 'new_status': new_status})
        except VendorPayoutRequest.DoesNotExist:
            return Response({'error': 'Payout request not found'}, status=404)
        


# =========================
#  Product
# =========================

@admin_required
def all_farmer_product_list(request):

    # Get all products with related data to optimize database queries
    farmer_products = FarmerProduct.objects.all().order_by('-created_at', '-updated_at')
    
    # Calculate overall aggregates for statistics cards
    aggregates = farmer_products.aggregate(
        total_quantity=Sum('quantity'),
        total_available=Sum('available_quantity')
    )
    

    # Get all verified farmers for the filter dropdown
    # Only include active and verified farmers who have products
    farmers = Farmer.objects.filter(
        is_active=True,
        verification_status='verified'
    ).select_related('user').order_by('farm_name')
    
    # Count active farmers who actually have products
    active_farmers_count = farmer_products.values('farmer').distinct().count()
    
    # Prepare context
    context = {
        'farmer_products': farmer_products,
        'aggregates': aggregates,
        'farmers': farmers,
        'active_farmers_count': active_farmers_count,
    }
    
    return render(request, 'admin_pages/product/all_farmer_products.html', context)



@admin_required
def all_vendor_product_list(request):
    # Get all vendor products with related data to avoid N+1 queries
    vendor_products = VendorProduct.objects.filter(vendor__is_active=True).select_related('vendor', 'farmer_product__category').order_by('-selected_at', '-delivered_at')
    
    # Calculate aggregates (use selected_quantity for VendorProduct)
    aggregates = vendor_products.aggregate(
        total_quantity=Sum('selected_quantity'),
        total_available=Sum('available_quantity')
    )
    
    # Get all verified and active vendors
    vendors = Vendor.objects.filter(
        is_active=True,
        verification_status='verified'
    ).select_related('user').order_by('shop_name')
    
    # Count unique vendors that have products
    active_vendors_count = vendor_products.values('vendor').distinct().count()
    
    # Get unique categories from vendor products (for filter dropdown)
    categories = vendor_products.values_list(
        'farmer_product__category__name',
        flat=True
    ).distinct().order_by('farmer_product__category__name')
    
    context = {
        'vendor_products': vendor_products,
        'aggregates': aggregates,
        'vendors': vendors,
        'active_vendors_count': active_vendors_count,
        'categories': categories,  # Add this for category filter
    }
    
    return render(request, 'admin_pages/product/all_vendor_products.html', context)


@admin_required
def category_list(request):
    categories = Category.objects.all().order_by('name')
    category_list=[]
    for category in categories:
        products_count=FarmerProduct.objects.filter(category=category).count()
        category.products_count=products_count
        category_list.append(category)
        
    
    total_categories = categories.count()
    total_categories_with_products = FarmerProduct.objects.values('category').distinct().count()
    return render(request, 'admin_pages/product/category_list.html', {'categories': category_list, 'total_categories': total_categories,'total_categories_with_products':total_categories_with_products})


@admin_required
def category_add(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name__iexact=name).exists():
            messages.error(request, f'Category "{name}" already exists.')
        else:
            Category.objects.create(name=name)
            messages.success(request, f'Category "{name}" added successfully.')
            return redirect('admin_category_list_page')
    return render(request, 'admin_pages/product/category_add.html')    


@admin_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name__iexact=name).exclude(id=category.id).exists():
            messages.error(request, f'Category "{name}" already exists.')
        else:
            category.name = name
            category.save()
            messages.success(request, f'Category "{name}" updated successfully.')
            return redirect('admin_category_list_page')
    context = {
        'category': category
    }
    return render(request, 'admin_pages/product/category_edit.html', context)


@admin_required
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    if FarmerProduct.objects.filter(category=category).exists():
        messages.error(request, f'Cannot delete category "{category.name}". There are products associated with it.')
    else:
        category.delete()
        messages.success(request, f'Category "{category.name}" deleted successfully.')
    return redirect('admin_category_list_page')



# =========================
#  Custom Views
# =========================
@admin_required
def customer_list(request):
    customers = UserRole.objects.filter(role='customer').select_related('user').order_by('-user__date_joined')
    total_customers = customers.count()
    customer_list=[]
    for customer in customers:
        total_orders=Order.objects.filter(user=customer.user).count()
        customer.total_orders=total_orders
        customer_list.append(customer)
    
    context = {
        'customers': customer_list,
        'total_customers': total_customers
    }
    return render(request, 'admin_pages/customer/customer_list.html', context)

@admin_required
def customer_delete(request, customer_id):
    customer_role = get_object_or_404(UserRole, id=customer_id, role='customer')
    if Order.objects.filter(user=customer_role.user, status__in=['pending', 'selected', 'in_transit']).exists():
        messages.error(request, f'Cannot delete customer "{customer_role.user.username}". There are active orders associated with this customer.')
        return redirect('admin_customer_list_page')
    user = customer_role.user
    user.is_active = False
    user.save()
    messages.success(request, f'Customer "{user.username}" deleted successfully.')
    return redirect('admin_customer_list_page')

# ========================
#  Reviews and Ratuings
# ========================
@admin_required
def review_list(request):
    review=Review.objects.all().order_by('-created_at')
    return render(request, 'admin_pages/review/review_list.html',{'reviews':review})

@admin_required
def review_delete(request,review_id):
    review=Review.objects.get(id=review_id)
    review.delete()
    messages.success(request,'Review deleted successfully')
    return redirect('admin_review_list_page')


# ============================
#  Finance
# ============================
@admin_required
def admin_wallet(request):
    # Get admin wallet
    admin_wallet = AdminWallet.objects.first()
    if not admin_wallet:
        admin_wallet = AdminWallet.objects.create()
    
    # Get all delivered and paid orders with related data
    orders = Order.objects.filter(
        status='delivered',
        payment_status='paid'
    ).select_related('user').order_by('-delivered_at')
    
    # Calculate total from orders
    total_income = orders.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    context = {
        'admin_wallet': admin_wallet,
        'orders': orders,
        'total_income': total_income,
        'total_orders': orders.count(),
    }
    return render(request, 'admin_pages/finance/admin_wallet.html', context)


@admin_required
def order_income_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    # Get order items with related vendor and farmer info
    order_items = order.items.all().select_related(
        'vendor_product__vendor',
        'vendor_product__farmer_product__farmer'
    )
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    return render(request, 'admin_pages/finance/order_income_detail.html', context)


@admin_required
def commission_rate(request):
    commission = CommissionRate.objects.first()
    if not commission:
        commission = CommissionRate.objects.create()
    
    context = {
        'commission': commission
    }
    return render(request, 'admin_pages/finance/commission_rate.html', context)


@admin_required
def commission_rate_edit(request):
    commission = CommissionRate.objects.first()
    if not commission:
        commission = CommissionRate.objects.create()
    
    if request.method == 'POST':
        try:
            rate = request.POST.get('rate')
            commission.rate = Decimal(rate)
            commission.save()
            messages.success(request, f'Commission rate updated to {rate}%')
            return redirect('admin_commission_rate_page')
        except Exception as e:
            messages.error(request, f'Error updating commission rate: {str(e)}')
    
    context = {
        'commission': commission
    }
    return render(request, 'admin_pages/wallet/commission_rate_edit.html', context)


def revenue_report(request):
    
    # Admin wallet and totals
    admin_wallet = AdminWallet.objects.first()
    if not admin_wallet:
        admin_wallet = AdminWallet.objects.create()

    total_revenue = Order.objects.filter(status='delivered', payment_status='paid').aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    total_orders = Order.objects.count()

    # Prepare last 12 months data
    today = timezone.now().date()
    monthly_revenue = []
    orders_by_month = []
    for months_ago in range(11, -1, -1):
        # compute year/month for months_ago
        y = today.year
        m = today.month - months_ago
        while m <= 0:
            m += 12
            y -= 1
        start = date(y, m, 1)
        if m == 12:
            end = date(y + 1, 1, 1)
        else:
            end = date(y, m + 1, 1)

        orders_qs = Order.objects.filter(
            status='delivered',
            payment_status='paid',
            delivered_at__gte=start,
            delivered_at__lt=end
        )
        month_total = orders_qs.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
        month_count = orders_qs.count()
        month_label = f"{calendar.month_abbr[m]} {y}"

        monthly_revenue.append({'month': month_label, 'total': float(month_total)})
        orders_by_month.append({'month': month_label, 'orders': month_count})

    # Commission breakdown (use admin wallet split if available)
    farmer_commission = float((admin_wallet.balance / 2) if admin_wallet.balance else 0)
    vendor_commission = float((admin_wallet.balance / 2) if admin_wallet.balance else 0)
    commission_breakdown = [
        {'name': 'Farmers', 'value': farmer_commission},
        {'name': 'Vendors', 'value': vendor_commission},
    ]

    # Top metrics
    farmer_products = FarmerProduct.objects.count()
    vendor_products = VendorProduct.objects.count()
    total_customers = UserRole.objects.filter(role='customer').count()

    context = {
        'admin_wallet': admin_wallet,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'monthly_revenue': monthly_revenue,
        'orders_by_month': orders_by_month,
        'commission_breakdown': commission_breakdown,
        'farmer_commission': farmer_commission,
        'vendor_commission': vendor_commission,
        'farmer_products': farmer_products,
        'vendor_products': vendor_products,
        'total_customers': total_customers,
    }
    return render(request, 'admin_pages/finance/revenue_report.html', context)


# ============================
#  Notifications
# ============================
def notification_list(request):
    from agroEcommerce.models import Notification
    # Show notifications for current user (admin) and allow marking all as read
    if request.method == 'POST' and request.POST.get('action') == 'mark_all_read':
        # Mark all unread notifications for this user as read
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('admin_notification_list_page')

    notifications = Notification.objects.filter(user=request.user).select_related('user').order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'total_notifications': notifications.count(),
    }
    return render(request, 'admin_pages/notifications/notification_list.html', context)


# ============================
#  Activity Logs
# ============================
def activity_logs_list(request):
    logs = AuditLog.objects.all().select_related('user').order_by('-created_at')
    
    context = {
        'logs': logs,
        'total_logs': logs.count(),
    }
    return render(request, 'admin_pages/audit/activity_logs.html', context)


# ============================
#  Organization
# ============================
def organization_view(request):
    
    organization = Organization.objects.first()
    if not organization:
        organization = Organization.objects.create(
            name='Agro Ecommerce',
            email='info@agroecommerce.com',
            phone='+977-1-1234567',
            address='Kathmandu, Nepal'
        )
    
    context = {
        'organization': organization
    }
    return render(request, 'admin_pages/settings/organization.html', context)


def organization_edit(request):
    
    organization = Organization.objects.first()
    if not organization:
        organization = Organization.objects.create(
            name='Agro Ecommerce',
            email='info@agroecommerce.com',
            phone='+977-1-1234567',
            address='Kathmandu, Nepal'
        )
    
    if request.method == 'POST':
        try:
            organization.name = request.POST.get('name')
            organization.email = request.POST.get('email')
            organization.phone = request.POST.get('phone')
            organization.address = request.POST.get('address')
            organization.facebook = request.POST.get('facebook', '')
            organization.instagram = request.POST.get('instagram', '')
            organization.twitter = request.POST.get('twitter', '')
            
            if request.FILES.get('logo'):
                organization.logo = request.FILES['logo']
            
            organization.save()
            messages.success(request, 'Organization information updated successfully')
            return redirect('admin_organization_page')
        except Exception as e:
            messages.error(request, f'Error updating organization: {str(e)}')
    
    context = {
        'organization': organization
    }
    return render(request, 'admin_pages/settings/organization_edit.html', context)


# ============================
#  Change Password
# ============================
from django.contrib.auth import update_session_auth_hash

@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validate old password
        if not request.user.check_password(old_password):
            messages.error(request, 'Your current password is incorrect.')
        # Check if new passwords match
        elif new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
        
        else:
            # Update password
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('admin_organization_page')
    
    context = {}
    return render(request, 'admin_pages/settings/change_password.html', context)

