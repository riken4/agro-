from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Q, F
from django.utils import timezone
from decimal import Decimal
from django.db import transaction
from django.contrib import messages
from agroEcommerce.models import (
    Farmer, FarmerProduct, FarmerWallet, FarmerPayoutRequest,
    VendorProduct, Order, OrderItems, AuditLog,Category,Notification
)
from datetime import datetime
from django.utils import timezone

# Create your views here.

def farmer_dashboard(request):
 
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        return redirect('home')  # Redirect if user is not a farmer
    
    # Get farmer's wallet
    farmer_wallet = FarmerWallet.objects.filter(farmer=farmer).first()
    wallet_balance = farmer_wallet.balance if farmer_wallet else Decimal('0.00')
    
    # Get all farmer's products
    farmer_products = FarmerProduct.objects.filter(farmer=farmer)
    total_products = farmer_products.count()
    
    # Get products by status
    pending_products = farmer_products.filter(delivery_status='pending').count()
    selected_products = farmer_products.filter(delivery_status='selected').count()
    in_transit_products = farmer_products.filter(delivery_status='in_transit').count()
    delivered_products = farmer_products.filter(delivery_status='delivered').count()
    
    # Calculate total quantity uploaded
    total_quantity_uploaded = farmer_products.aggregate(
        total=Sum('quantity')
    )['total'] or Decimal('0.00')
    
    # Calculate total available quantity
    total_available_quantity = farmer_products.aggregate(
        total=Sum('available_quantity')
    )['total'] or Decimal('0.00')
    
    # Get vendor selections of farmer's products
    vendor_selections = VendorProduct.objects.filter(
        farmer_product__farmer=farmer
    ).select_related('vendor', 'farmer_product')
    
    # Calculate total revenue from delivered products
    # Revenue = quantity sold * base price (before commission)
    delivered_items = OrderItems.objects.filter(
        vendor_product__farmer_product__farmer=farmer,
        order__status='delivered',
        order__payment_status='paid'
    ).select_related('order', 'vendor_product__farmer_product')
    
    total_revenue = Decimal('0.00')
    for item in delivered_items:
        farmer_product = item.vendor_product.farmer_product
        item_revenue = farmer_product.base_price * item.quantity
        total_revenue += item_revenue
    
    # Get total earnings (actual amount credited to wallet after commission)
    total_earnings = wallet_balance  # Current balance reflects total earnings
    
    # Count total orders containing farmer's products
    total_orders = Order.objects.filter(
        items__vendor_product__farmer_product__farmer=farmer,
        status='delivered'
    ).distinct().count()
    
    # Recent vendor selections (last 5)
    recent_selections = vendor_selections.order_by('-selected_at')[:5]
    
    # Recent products (last 5)
    recent_products = farmer_products.order_by('-created_at')[:5]
    
    # Pending payout requests
    pending_payouts = FarmerPayoutRequest.objects.filter(
        farmer=farmer,
        status='pending'
    ).count()
    
    # Recent payout requests (last 5)
    recent_payouts = FarmerPayoutRequest.objects.filter(
        farmer=farmer
    ).order_by('-created_at')[:5]
    
    # Products expiring soon (within 7 days)
    expiring_soon = farmer_products.filter(
        expiry_date__lte=timezone.now().date() + timezone.timedelta(days=7),
        expiry_date__gte=timezone.now().date(),
        delivery_status='pending'
    ).count()
    
    # Products expired
    expired_products = farmer_products.filter(
        expiry_date__lt=timezone.now().date()
    ).count()
    
    # Monthly statistics (current month)
    current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    monthly_products_added = farmer_products.filter(
        created_at__gte=current_month_start
    ).count()
    
    monthly_selections = vendor_selections.filter(
        selected_at__gte=current_month_start
    ).count()
    
    monthly_revenue = Decimal('0.00')
    monthly_items = delivered_items.filter(
        order__created_at__gte=current_month_start
    )
    for item in monthly_items:
        farmer_product = item.vendor_product.farmer_product
        item_revenue = farmer_product.base_price * item.quantity
        monthly_revenue += item_revenue
    
    # Recent audit logs for farmer
    recent_activities = AuditLog.objects.filter(
        Q(user=farmer.user) | 
        Q(description__icontains=farmer.farm_name)
    ).order_by('-created_at')[:10]
    
    context = {
        'farmer': farmer,
        'wallet_balance': wallet_balance,
        'total_products': total_products,
        'pending_products': pending_products,
        'selected_products': selected_products,
        'in_transit_products': in_transit_products,
        'delivered_products': delivered_products,
        'total_quantity_uploaded': total_quantity_uploaded,
        'total_available_quantity': total_available_quantity,
        'total_revenue': total_revenue,
        'total_earnings': total_earnings,
        'total_orders': total_orders,
        'recent_selections': recent_selections,
        'recent_products': recent_products,
        'pending_payouts': pending_payouts,
        'recent_payouts': recent_payouts,
        'expiring_soon': expiring_soon,
        'expired_products': expired_products,
        'monthly_products_added': monthly_products_added,
        'monthly_selections': monthly_selections,
        'monthly_revenue': monthly_revenue,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'farmer_pages/farmer_dashboard.html', context)



# =====================
#   Farmer Products
# ===================

def farmer_products_all(request):
    farmer=request.user.farmer
    products=FarmerProduct.objects.filter(farmer=farmer).select_related('category').order_by('-created_at')
    
    # Calculate statistics
    total_products =products.count()
    pending_products=products.filter(delivery_status='pending').count()
    
    # Total quantity uploaded
    total_quantity= products.aggregate(
        total=Sum('quantity')
    )['total'] or Decimal('0.00')
    
    # Total available quantity
    total_available= products.aggregate(total=Sum('available_quantity'))['total'] or Decimal('0.00')
    
    # Get all Categories 
    categories= Category.objects.all().order_by('name')
    context = {
        'products': products,
        'total_products': total_products,
        'pending_products': pending_products,
        'total_quantity': total_quantity,
        'total_available': total_available,
        'categories': categories,
        'farmer': farmer,
    }
    
    return render(request, 'farmer_pages/products/all_products.html', context)



def farmer_product_detail(request, product_id):
 
    
    return render(request, 'farmer_pages/products/product_details.html')


def farmer_add_product(request):
    farmer=request.user.farmer
    
    if request.method == 'POST':
        try:
            name=request.POST.get('name')
            categoy_id=request.POST.get('category')
            quality=request.POST.get('quanlity')
            description=request.POST.get('description')
            quantity=request.POST.get('quantity')
            base_price=request.POST.get('base_price')
            harvest_date=request.POST.get('harvest_date')
            expiry_date=request.POST.get('expiry_date')
            image=request.FILES.get('image')
            
            category=Category.objects.get(id=categoy_id)
            
            expiry_date_obj=datetime.strptime(expiry_date, '%Y-%m-%d').date()
            if expiry_date_obj < timezone.now().date():
                messages.error(request,'Expiry date musb be in future')
                return redirect('farmer_product_add')
            harvest_date_obj=datetime.strptime(harvest_date,'%Y-%m-%d').date()
            if harvest_date_obj > timezone.now().date():
                messages.error(request,'Harvest date cannot  be in the future')
                return redirect('farmer_product_add')
            
            product=FarmerProduct.objects.create(
                farmer=farmer,
                category=category,
                name=name,
                description=description,
                image=image,
                quantity=quality,
                quality=quality,
                available_quantity=quantity,
                base_price=base_price,
                expiry_date=expiry_date_obj,
                harvest_date=harvest_date_obj,
                delivery_status='pending'
                
            )
            Notification.objects.create(
                user=request.user,
                notification_type='product',
                title='Product Added Successfully',
                message=f'Your Product {name} has been added'
                                
            )
            AuditLog.objects.create(
                user=request.user,
                action='product_added',
                description=f'Added product:{name} -  {quantity}kg as Rs.{base_price}/kg',
                ip_address=request.META.get('REMOTE_ADDR')
                
            )
            messages.success(request,f'Product {product.name} has been added successfully')
            return redirect('farmer_products_all')
            
        except Exception as e:
            messages.error(request,"Error in adding product")
            return redirect('farmer_product_add')
    return render(request,'farmer_pages/products/add_product.html')



#  Farmer edit product
def farmer_edit_product(request,product_id):
    farmer=request.user
    product=FarmerProduct.objects.get(farmer=farmer,id=product_id)
    if product.delivery_status != 'pending':
        messages.error(request,'You can  only edit products with pending status')
        return redirect('farmer_product_edit')
    
    if request.method == 'POST':
        try:
            name=request.POST.get('name')
            category_id=request.POST.get('category_id')
            quality= request.POST.get('quality')
            description=request.POST.get('description')
            quantity=request.POST.get('quantity')
            base_price=request.POST.get('base_price')
            harvest_date=request.POST.get('harvest_date')
            expiry_date=request.POST.get('expiry_date')
            image=request.FILES.get('image')
            
            expiry_date_obj=datetime.strptime(expiry_date, '%Y-%m-%d').date()
            if expiry_date_obj < timezone.now().date():
                messages.error(request,'Expiry date musb be in future')
                return redirect('farmer_product_edit')
            harvest_date_obj=datetime.strptime(harvest_date,'%Y-%m-%d').date()
            if harvest_date_obj > timezone.now().date():
                messages.error(request,'Harvest date cannot  be in the future')
                return redirect('farmer_product_edit')
            
            quantity_difference= quantity - product.quantity
            category=Category.objects.get(id=category_id)
            
            product.name=name
            product.category=category
            product.description=description
            product.quality=quality
            product.quantity=quantity
            product.available_quantity += quantity_difference
            product.base_price = base_price
            product.expiry_date = expiry_date_obj
            product.harvest_date = harvest_date_obj
            
            if image:
                product.image= image
            product.save()
            
            Notification.objects.create(
                user=request.user,
                notification_type='product',
                title='Product Updated Sucessfully',
                message= f'Your  product {name} has been updated'
            )
            
            AuditLog.objects.create(
                user=request.user,
                action='product_updated',
                description=f'Updated product {name} - {quantity}kg at Rs.{base_price}/kg',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            messages.success(request,f'Product {name} has been updated successfully')
            return redirect('farmer_products_all')
    
        except Exception as e:
            messages.error(request,'Error in editing the product')
    return render(request,'farmer_pages/products/edit_product.html')




def  farmer_product_delete(request,product_id):
    farmer=request.user.farmer
    product=FarmerProduct.objects.get(farmer=farmer,id=product_id)
    
    can_delete=True
    vendor_selections=VendorProduct.objects.filter(farmer_product=product)
    if vendor_selections.exists():
        can_delete=False
    
    if product.delivery_status != 'pending':
        can_delete=False
    
    if not can_delete:
        messages.error(request,'Cannot delete this product. You can only delete products that are pending and has not selected by vendors')
        return redirect('farmer_products_all')
    try:
        if request.method == 'POST':
            product_name=product.name
            with transaction.atomic():
                AuditLog.objects.create(
                    user=request.user,
                    action='product_deleted',
                    description=f'Deleted product: {product_name}',
                    ip_address=request.META.get('REMOTE_ADDR')
                )
                product.delete()
                Notification.objects.create(
                    user=request.user,
                    notification_type='Product Deleted',
                    message=f'Product {product_name}  has been deleted successfully'
                )
                messages.success(request,f'Product {product_name} deleted successfully')
                return redirect('farmer_products_all')
    except Exception as e:
        messages.error(request,f"Error deleting product : {str(e)}")
        return redirect('farmer_products_all')
    
        
            
    
        

@login_required
def farmer_pending_products(request):
    """Display all pending products waiting for vendor selection"""
    
    # Check if user is a farmer
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        messages.error(request, "You must be a registered farmer to access this page.")
        return redirect('home')
    
    # Get all pending products for this farmer
    products = FarmerProduct.objects.filter(
        farmer=farmer,
        delivery_status='pending'
    ).select_related('category').order_by('-created_at')
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    # Calculate statistics
    total_products = products.count()
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or Decimal('0')
    total_available = products.aggregate(Sum('available_quantity'))['available_quantity__sum'] or Decimal('0')
    
    # Calculate total value
    total_value = sum([
        (product.base_price * product.quantity) 
        for product in products
    ])
    
    # Count expired products
    expired_count = products.filter(expiry_date__lt=timezone.now().date()).count()
    
    # Count products expiring soon (within 7 days)
    expiring_soon_count = products.filter(
        expiry_date__gte=timezone.now().date(),
        expiry_date__lte=timezone.now().date() + timezone.timedelta(days=7)
    ).count()
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_available': total_available,
        'total_value': total_value,
        'expired_count': expired_count,
        'expiring_soon_count': expiring_soon_count,
        'page_title': 'Pending Products',
        'page_description': 'Products waiting for vendor selection',
    }
    
    return render(request, 'farmer_pages/products/pending_products.html', context)


@login_required
def farmer_selected_products(request):
    """Display all products that have been selected by vendors"""
    
    # Check if user is a farmer
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        messages.error(request, "You must be a registered farmer to access this page.")
        return redirect('home')
    
    # Get all non-pending products (selected, in_transit, delivered)
    products = FarmerProduct.objects.filter(
        farmer=farmer
    ).exclude(
        delivery_status='pending'
    ).exclude(
        delivery_status='cancelled'
    ).select_related('category').prefetch_related(
        'vendor_selections',
        'vendor_selections__vendor'
    ).order_by('-updated_at')
    
    # Get all categories for filter
    categories = Category.objects.all()
    
    # Calculate statistics
    total_products = products.count()
    
    # Get vendor selections for these products
    vendor_selections = VendorProduct.objects.filter(
        farmer_product__farmer=farmer
    ).exclude(
        farmer_product__delivery_status='pending'
    ).select_related('vendor', 'farmer_product')
    
    # Calculate selected quantities
    total_selected_quantity = vendor_selections.aggregate(
        Sum('selected_quantity')
    )['selected_quantity__sum'] or Decimal('0')
    
    # Calculate total value from selections
    total_value = sum([
        (selection.farmer_product.base_price * selection.selected_quantity)
        for selection in vendor_selections
    ])
    
    # Count unique vendors
    unique_vendors = vendor_selections.values('vendor').distinct().count()
    
    # Count by status
    selected_count = products.filter(delivery_status='selected').count()
    in_transit_count = products.filter(delivery_status='in_transit').count()
    delivered_count = products.filter(delivery_status='delivered').count()
    
    context = {
        'products': products,
        'categories': categories,
        'vendor_selections': vendor_selections,
        'total_products': total_products,
        'total_selected_quantity': total_selected_quantity,
        'total_value': total_value,
        'unique_vendors': unique_vendors,
        'selected_count': selected_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'page_title': 'Selected Products',
        'page_description': 'Products selected by vendors',
    }
    
    return render(request, 'farmer_pages/products/selected_products.html', context)


@login_required
def farmer_vendor_selections_detail(request, product_id):
    """Display detailed vendor selections for a specific product"""
    
    # Check if user is a farmer
    try:
        farmer = request.user.farmer
    except Farmer.DoesNotExist:
        messages.error(request, "You must be a registered farmer to access this page.")
        return redirect('home')
    
    # Get the product
    try:
        product = FarmerProduct.objects.get(id=product_id, farmer=farmer)
    except FarmerProduct.DoesNotExist:
        messages.error(request, "Product not found.")
        return redirect('farmer_products_list')
    
    # Get all vendor selections for this product
    selections = VendorProduct.objects.filter(
        farmer_product=product
    ).select_related('vendor').order_by('-selected_at')
    
    # Calculate totals
    total_selected = selections.aggregate(
        Sum('selected_quantity')
    )['selected_quantity__sum'] or Decimal('0')
    
    total_revenue = sum([
        (product.base_price * selection.selected_quantity)
        for selection in selections
    ])
    
    context = {
        'product': product,
        'selections': selections,
        'total_selected': total_selected,
        'total_revenue': total_revenue,
       
    }
    
    return render(request, 'farmer_pages/products/vendor_selections_detail.html', context)