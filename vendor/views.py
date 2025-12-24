from django.shortcuts import render
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
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser


# Create your views here.
def vendor_dashboard(request):
    # Gather vendor-specific metrics similar to admin dashboard
    vendor = getattr(request.user, 'vendor', None)
    if not vendor:
        messages.error(request, 'Vendor profile not found')
        return render(request, 'vendor_pages/vendor_dashboard.html', {})

    from django.db.models import Sum,Avg,F,ExpressionWrapper,DecimalField
    from decimal import Decimal
    from agroEcommerce.models import OrderItems

    # Total revenue for this vendor (delivered & paid orders)
    revenue_expr = ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField())
    revenue_agg = OrderItems.objects.filter(vendor_product__vendor=vendor,
                                            order__status='delivered',
                                            order__payment_status='paid')
    total_revenue = revenue_agg.aggregate(total=Sum(revenue_expr))['total'] or Decimal('0.00')

    # Total orders containing this vendor's products
    total_orders = Order.objects.filter(items__vendor_product__vendor=vendor).distinct().count()

    # Pending orders count
    pending_orders_count = Order.objects.filter(status='pending', items__vendor_product__vendor=vendor).distinct().count()

    # Total vendor products
    total_products = VendorProduct.objects.filter(vendor=vendor).count()

    # Average rating and review count
    avg_rating = Review.objects.filter(vendor_product__vendor=vendor).aggregate(avg=Avg('rating'))['avg'] or 0
    reviews_count = Review.objects.filter(vendor_product__vendor=vendor).count()

    # Wallet balance
    try:
        wallet_balance = vendor.vendor_wallet.balance
    except Exception:
        wallet_balance = Decimal('0.00')

    # Recent orders (latest 5)
    recent_orders = Order.objects.filter(items__vendor_product__vendor=vendor).distinct().order_by('-created_at')[:5]

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders_count': pending_orders_count,
        'total_products': total_products,
        'avg_rating': avg_rating,
        'reviews_count': reviews_count,
        'vendor_wallet_balance': wallet_balance,
        'recent_orders': recent_orders,
    }

    return render(request,'vendor_pages/vendor_dashboard.html', context)


# --- Products ---
@login_required
def vendor_products_all(request):
    vendor = getattr(request.user, 'vendor', None)
    products = VendorProduct.objects.filter(vendor=vendor).select_related('farmer_product__farmer')
    
    # Aggregates
    total_products = products.count()
    total_quantity = products.aggregate(Sum('selected_quantity'))['selected_quantity__sum'] or Decimal('0.00')
    total_available = products.aggregate(Sum('available_quantity'))['available_quantity__sum'] or Decimal('0.00')
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_available': total_available,
    }
    return render(request, 'vendor_pages/products/all_products.html', context)


@login_required
def vendor_products_available(request):
    vendor = getattr(request.user, 'vendor', None)
    products = VendorProduct.objects.filter(vendor=vendor, is_available_for_customers=True).select_related('farmer_product__farmer')
    
    total_products = products.count()
    total_quantity = products.aggregate(Sum('selected_quantity'))['selected_quantity__sum'] or Decimal('0.00')
    total_available = products.aggregate(Sum('available_quantity'))['available_quantity__sum'] or Decimal('0.00')
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_available': total_available,
    }
    return render(request, 'vendor_pages/products/available_products.html', context)


@login_required
def vendor_products_in_transit(request):
    vendor = getattr(request.user, 'vendor', None)
    products = VendorProduct.objects.filter(vendor=vendor, delivery_status='in_transit').select_related('farmer_product__farmer')
    
    total_products = products.count()
    total_quantity = products.aggregate(Sum('selected_quantity'))['selected_quantity__sum'] or Decimal('0.00')
    total_available = products.aggregate(Sum('available_quantity'))['available_quantity__sum'] or Decimal('0.00')
    
    context = {
        'products': products,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_available': total_available,
    }
    return render(request, 'vendor_pages/products/in_transit.html', context)


@login_required
def vendor_product_detail(request, pk):
    vendor = getattr(request.user, 'vendor', None)
    product = get_object_or_404(VendorProduct.objects.select_related('farmer_product__farmer'), pk=pk, vendor=vendor)
    reviews = Review.objects.filter(vendor_product=product).order_by('-created_at')
    context = {'product': product, 'reviews': reviews}
    return render(request, 'vendor_pages/products/product_detail.html', context)


# --- Warehouse ---
@login_required
def vendor_browse_warehouse(request):
    # show farmer products that still have available quantity
    farmer_products = FarmerProduct.objects.filter(available_quantity__gt=0).select_related('farmer')[:100]
    total_products = farmer_products.count()
    total_quantity = farmer_products.aggregate(Sum('available_quantity'))['available_quantity__sum'] or Decimal('0.00')
    context = {'farmer_products': farmer_products, 'total_products': total_products, 'total_quantity': total_quantity}
    return render(request, 'vendor_pages/browse_warehouse.html', context)


@login_required
def vendor_warehouse_detail(request, pk):
    fp = get_object_or_404(FarmerProduct.objects.select_related('farmer'), pk=pk)
    context = {'farmer_product': fp}
    return render(request, 'vendor_pages/warehouse/warehouse_detail.html', context)


# --- Orders ---
@login_required
def vendor_orders_all(request):
    vendor = getattr(request.user, 'vendor', None)
    orders = Order.objects.filter(items__vendor_product__vendor=vendor).distinct().order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'vendor_pages/orders/all_orders.html', context)



@login_required
def vendor_orders_pending(request):
    vendor = getattr(request.user, 'vendor', None)
    orders = Order.objects.filter(status='pending', items__vendor_product__vendor=vendor).distinct().order_by('-created_at')
    total_value = orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'orders': orders, 'total_value': total_value}
    return render(request, 'vendor_pages/orders/pending_orders.html', context)


@login_required
def vendor_orders_processing(request):
    vendor = getattr(request.user, 'vendor', None)
    orders = Order.objects.filter(status='processing', items__vendor_product__vendor=vendor).distinct().order_by('-created_at')
    total_value = orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'orders': orders, 'total_value': total_value}
    return render(request, 'vendor_pages/orders/processing_orders.html', context)


@login_required
def vendor_orders_shipped(request):
    vendor = getattr(request.user, 'vendor', None)
    orders = Order.objects.filter(status='shipped', items__vendor_product__vendor=vendor).distinct().order_by('-created_at')
    total_value = orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'orders': orders, 'total_value': total_value}
    return render(request, 'vendor_pages/orders/shipped_orders.html', context)


@login_required
def vendor_orders_delivered(request):
    vendor = getattr(request.user, 'vendor', None)
    orders = Order.objects.filter(status='delivered', items__vendor_product__vendor=vendor).distinct().order_by('-created_at')
    total_value = orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'orders': orders, 'total_value': total_value}
    return render(request, 'vendor_pages/orders/delivered_orders.html', context)


@login_required
def vendor_order_detail(request, order_id):
    vendor = getattr(request.user, 'vendor', None)
    order = get_object_or_404(Order, pk=order_id, items__vendor_product__vendor=vendor)
    # show only items for this vendor
    items = order.items.filter(vendor_product__vendor=vendor).select_related('vendor_product__farmer_product')
    context = {'order': order, 'items': items}
    return render(request, 'vendor_pages/orders/order_detail.html', context)


# --- Finance ---
@login_required
def vendor_finance_wallet(request):
    vendor = getattr(request.user, 'vendor', None)
    if not vendor:
        return redirect('vendor_dashboard')
    wallet = vendor.vendor_wallet
    # Get recent orders for commission calculation
    recent_orders = Order.objects.filter(items__vendor_product__vendor=vendor, status='delivered').distinct().order_by('-created_at')[:50]
    total_revenue = recent_orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'wallet': wallet, 'wallet_balance': wallet.balance, 'total_revenue': total_revenue, 'recent_orders': recent_orders}
    return render(request, 'vendor_pages/finance/wallet.html', context)


@login_required
def vendor_finance_payouts(request):
    vendor = getattr(request.user, 'vendor', None)
    if not vendor:
        return redirect('vendor_dashboard')
    wallet = vendor.vendor_wallet
    # Simulate payout requests (can be extended with a PayoutRequest model)
    context = {'wallet_balance': wallet.balance, 'payout_requests': []}
    return render(request, 'vendor_pages/finance/payout_requests.html', context)


@login_required
def vendor_finance_earnings(request):
    vendor = getattr(request.user, 'vendor', None)
    if not vendor:
        return redirect('vendor_dashboard')
    # Get all delivered orders for this vendor
    delivered_orders = Order.objects.filter(items__vendor_product__vendor=vendor, status='delivered').distinct().order_by('-created_at')
    total_earned = delivered_orders.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_orders = delivered_orders.count()
    # Get monthly earnings
    from django.utils import timezone
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_earnings = Order.objects.filter(items__vendor_product__vendor=vendor, status='delivered', created_at__gte=thirty_days_ago).distinct().aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    context = {'total_earned': total_earned, 'total_orders': total_orders, 'recent_earnings': recent_earnings, 'delivered_orders': delivered_orders[:100]}
    return render(request, 'vendor_pages/finance/earnings_report.html', context)


# --- Reviews / Notifications / Settings / Profile ---
@login_required
def vendor_reviews(request):
    return render(request, 'vendor_pages/reviews.html')


@login_required
def vendor_notifications(request):
    return render(request, 'vendor_pages/notifications.html')


@login_required
def vendor_shop_settings(request):
    return render(request, 'vendor_pages/settings/shop_settings.html')


@login_required
def vendor_profile(request):
    return render(request, 'vendor_pages/profile.html')

