from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid



# ====================================
#   OTP verification
# =============================
class OTPVerification(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp_code=models.CharField(max_length=6,null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"OTP for {self.user.email}"
    

# =========================
#   User Role Management
# =========================
class UserRole(models.Model):
    ROLE_CHOICES=[
        ('customer','Customer'),
        ('vendor','Vendor'),
        ('farmer','Farmer'),
        ('admin','Admin'),
    ]
    
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='role')
    role=models.CharField(max_length=20,choices=ROLE_CHOICES,default='customer')
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name} -{self.role}"
    
    def is_customer(self):
        return self.role == 'customer'
    
    def is_vendor(self):
        return self.role == 'vendor'
    
    def is_farmer(self):
        return self.role == 'farmer'
    
    def is_admin(self):
        return self.role == 'admin'
    
# ================================
#   User Profile

class UserProfile(models.Model):
    GENDER_CHOICES=[
        ('male','Male'),
        ('female','Female'),
        ('other','Other')
    ]
    
    PROVINCE_CHOICES=[
        ('koshi','Koshi Province'),
        ('madesh','Madesh Province'),
        ('bagmati','Bagmanti Province'),
        ('gandaki','Gandaki Province'),
        ('lumbini','Lumbini Province'),
        ('karnali','Karnali Province'),
        ('sudurpaschim','Sudurpaschim Province'),
        
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="profile")
    phone=models.CharField(max_length=15,null=True,blank=True)
    avatar=models.ImageField(upload_to='avatar/',blank=True,null=True)
    gender=models.CharField(max_length=10,choices=GENDER_CHOICES,null=True,blank=True)
    
    address=models.TextField(blank=True)
    city=models.CharField(max_length=100,blank=True)
    province=models.CharField(max_length=50,choices=PROVINCE_CHOICES,null=True,blank=True)
    
    def __str__(self):
        return f"{self.user.get_full_name} 's  Profile"
    
    def get_role(self):
        try:
            return self.user.role.role
        except :
            return 'No Role Assigned'
        

# ======================================
#   Farmer Management
# ======================================
class Farmer(models.Model):
    PROVINCE_CHOICES = [
        ('koshi', 'Koshi Province'),
        ('madhesh', 'Madhesh Province'),
        ('bagmati', 'Bagmati Province'),
        ('gandaki', 'Gandaki Province'),
        ('lumbini', 'Lumbini Province'),
        ('karnali', 'Karnali Province'),
        ('sudurpashchim', 'Sudurpashchim Province'),
    ]
    
    VERIFICATION_STATUS= [
        ('pending','Pending '),
        ('verified','Verified'),
        ('rejected','rejected'),
    ]
    
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='farmer')
    
    # Basic Info
    farm_name=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    
    # Contact
    phone=models.CharField(max_length=15)
    address=models.TextField()
    city=models.CharField(max_length=100)
    province=models.CharField(max_length=20,choices=PROVINCE_CHOICES)
    
    # KYC Documents
    pan_number=models.CharField(max_length=15,unique=True)
    pan_document= models.FileField(upload_to='kyc/garmer/pan/')
    citizenship_number=models.CharField(max_length=20,blank=True)
    citizenship_front=models.FileField(upload_to='kyc/farmer/citizenship/',blank=True)
    citizenship_back=models.FileField(upload_to='kyc/farmer/citizenship/',blank=True)
    
    # payment qr image
    qr_image=models.ImageField(blank=True,upload_to="farmer/qr/")
    
    # Status
    verification_status=models.CharField(max_length=20,choices=VERIFICATION_STATUS,default='pending')
    rejection_reason=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    verified_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.farm_name
    


# =================================
#   Farmer Wallet
# =================================

class FarmerWallet(models.Model):
    farmer=models.OneToOneField(Farmer,on_delete=models.CASCADE,related_name='farmer_wallet')
    balance=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.farmer.farm_name} - Balance Rs {self.balance}"
    
    def credit(self,amount):
        self.balance += Decimal(amount)
        self.save()
        
    def debit(self,amount):
        if self.balance >=Decimal(amount):
            self.balance -= Decimal(amount)
            self.save()
            return True
        return False
    
# ===============================
#   Farmer Payout Request
# ===============================
class FarmerPayoutRequest(models.Model):
    STATUS_CHOICES=[
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('paid','Paid'),
    ]
    
    farmer=models.ForeignKey(Farmer,on_delete=models.CASCADE,related_name='payout_requests')
    requested_amount=models.DecimalField(max_digits=12,decimal_places=2)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    admin_response=models.TextField(blank=True)
    created_at=models.DateField(auto_now_add=True)
    paid_at=models.DateTimeField(null=True,blank=True)
    
    def __str__(self):
        return f"{self.farmer.farm_name} - Rs {self.requested_amount} ({self.status})"
    
# =============================
#   Vendor Management
# =============================
class Vendor(models.Model):
    PROVINCE_CHOICES = [
        ('koshi', 'Koshi Province'),
        ('madhesh', 'Madhesh Province'),
        ('bagmati', 'Bagmati Province'),
        ('gandaki', 'Gandaki Province'),
        ('lumbini', 'Lumbini Province'),
        ('karnali', 'Karnali Province'),
        ('sudurpashchim', 'Sudurpashchim Province'),
    ]
    
    VERIFICATION_STATUS= [
        ('pending','Pending'),
        ('verified','Verified'),
        ('rejected','Rejected')
    ]
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='vendor')
    
    # Shop Info
    shop_name=models.CharField(max_length=200)
    shop_logo=models.ImageField(upload_to='vendor_logos/',blank=True,null=True)
    description=models.TextField(blank=True)
    
    # Contact
    phone=models.CharField(max_length=15)
    address=models.TextField()
    city=models.CharField(max_length=100)
    province=models.CharField(max_length=20,choices=PROVINCE_CHOICES)
    
    qr_image=models.ImageField(blank=True,upload_to="vendor/qr/")
    # KYC 
    pan_number=models.CharField(max_length=15,unique=True)
    pan_document=models.FileField(upload_to='kyc/vendor/pan')
    
    # Status
    verification_status=models.CharField(max_length=20,choices=VERIFICATION_STATUS,default='pending')
    rejection_reason=models.TextField(blank=True)
    is_active=models.BooleanField(default=True)
    verified_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.shop_name
    
    
# ==================================
#   Vendor Wallet
# =================================
class VendorWallet(models.Model):
    vendor=models.OneToOneField(Vendor,on_delete=models.CASCADE,related_name='vendor_wallet')
    balance=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.vendor.shop_name} -- Balance Rs {self.balance}"
    
    def credit(self,amount):
        self.balance += Decimal(amount)
        self.save()
        
    def debit(self,amount):
        if self.balance >= Decimal(amount):
            self.balance -=Decimal(amount)
            self.save()
            return True
        return False
        

# ========================
#  Vendor Payout Request
# ========================
class VendorPayoutRequest(models.Model):
    STATUS_CHOICES= [
        ('pending','Pending'),
        ('approved','Approved'),
        ('rejected','Rejected'),
        ('paid','Paid'),
    ]
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE,related_name="payout_requests")
    requested_amount=models.DecimalField(max_digits=12,decimal_places=2)
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    admin_response=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    paid_at=models.DateTimeField(null=True,blank=True)
    
    def __str__(self):
        return f"{self.vendor.shop_name} - Rs.{self.requested_amount} - {self.status}"
    
# ==========================
#  Admin Wallet
# ==========================
class AdminWallet(models.Model):
    balance=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Admin Wallet - Balance Rs.{self.balance}"
    
    def credit(self,amount):
        self.balance += Decimal(amount)
        self.save()
    

# =========================
#  Commission Rate
# =========================
class CommissionRate(models.Model):
    rate = models.DecimalField(max_digits=5,decimal_places=2,default=Decimal('5.00'))
    created_at=models.DateTimeField(auto_now_add=True)
    
    def get_commission_amounts(self,total_amount):
        """  Return farmer_commission , vednor_commission , total_commission"""
        commission_rate=CommissionRate.objects.first()
        if not commission_rate:
            return Decimal('0.00'), Decimal('0.00'),Decimal(0.00)
        rate=commission_rate.rate / Decimal('100')
        half_rate = rate/2
        
        farmer_commission = total_amount * half_rate
        vendor_commission =  total_amount * half_rate
        total_commission= farmer_commission + vendor_commission
        return farmer_commission,  vendor_commission, total_commission
    
    def __str__(self):
        return f"{self.rate}%"


# =========================
#  Category Managemnet
# =========================
class Category(models.Model):
    name=models.CharField(max_length=100)
    
    
    def __str__(self):
        return self.name
    
# ================================
#  FarmerProduct (WareHouse Stock)
# ================================
class FarmerProduct(models.Model):
    QUALITY_CHOICES=[
        ('A','Grade A - Premium'),
        ('B','Grade B - Standard'),
        ('C','Grade C - Economy')
    ]    
    
    DELIVERY_STATUS=[
        ('pending','Pending'),
        ('selected','Selected'),
        ('in_transit','In Transit'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    ]
    farmer=models.ForeignKey(Farmer,on_delete=models.CASCADE,related_name="farmer_products")
    category = models.ForeignKey(Category,on_delete=models.SET_NULL,null=True,blank=True)
    
    #  Product Info
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True)
    image=models.ImageField(upload_to='farmer_products/')
    
    # Quantity & Quality
    quantity=models.DecimalField(max_digits=10,decimal_places=2)
    available_quantity=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    quality=models.CharField(max_length=10,choices=QUALITY_CHOICES)
    
    base_price=models.DecimalField(max_digits=10,decimal_places=2)
    
    #Date
    expiry_date=models.DateField()
    harvest_date=models.DateField(null=True,blank=True)
    
    # Delivery Status
    delivery_status=models.CharField(max_length=20,choices=DELIVERY_STATUS,default='pending')
    
    # Timestamps
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def is_available(self):
        if self.delivery_status == 'pending' and self.available_quantity > 0 and self.expiry_date >= timezone.now().date():
            return True
        else:
            return False
    
    
    def is_expired(self):
        return self.expiry_date < timezone.now().date()
    
    def __str__(self):
        return f"{self.name} - {self.farmer.farm_name}"
    
    
    def save(self,*args,**kwargs):
        if self.pk is None:
            self.available_quantity =self.quality
            
        super().save(*args,**kwargs)
        
    

# ===============================
#   Vendor Product Selection
# ===============================
class VendorProduct(models.Model):
    vendor=models.ForeignKey(Vendor,on_delete=models.CASCADE,related_name='selected_products')
    farmer_product=models.ForeignKey(FarmerProduct,on_delete=models.CASCADE,related_name="vendor_selections")
    
    # Selection Details
    selected_quantity=models.DecimalField(max_digits=10,decimal_places=2)
    selling_price=models.DecimalField(max_digits=10,decimal_places=2)
    
    #  Delivery tracking 
    delivery_status=models.CharField(max_length=20,choices=FarmerProduct.DELIVERY_STATUS,default='selected')
    
    # Stock tracking
    available_quantity=models.DecimalField(max_digits=10,decimal_places=2)
    
    # make visible to customers only after delivery
    is_available_for_customers=models.BooleanField(default=False)
    
    # Timestamps
    selected_at=models.DateTimeField(auto_now_add=True)
    delivered_at=models.DateTimeField(null=True,blank=True)
    
    def vendor_profit(self):
        return self.selling_price - self.farmer_product.base_price
    
    def total_vendor_profit(self):
        return self.vendor_profit() * self.selected_quantity
    
    
    def  save(self,*args,**kwargs):
        if not self.pk:
            self.available_quantity =self.selected_quantity
        
        if self.delivery_status == 'delivered' and self.available_quantity>0:
            self.is_available_for_customers=True
        
        if self.delivery_status == 'delivered' and not self.delivered_at:
            self.delivered_at=timezone.now()
        super.save(*args,**kwargs)
        
            
    def __str__(self):
        return f"{self.vendor.shop_name} - {self.farmer_product.name} {self.selected_quantity}"


# ===============================
#   Customer Order
# ===============================
class Order(models.Model):
    
    PROVINCE_CHOICES = [
        ('koshi', 'Koshi Province'),
        ('madhesh', 'Madhesh Province'),
        ('bagmati', 'Bagmati Province'),
        ('gandaki', 'Gandaki Province'),
        ('lumbini', 'Lumbini Province'),
        ('karnali', 'Karnali Province'),
        ('sudurpashchim', 'Sudurpashchim Province'),
    ]
    STATUS_CHOICES=[
        ('pending','Pending'),
        ('processing','Processing'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
    ]
    
    PAYMENT_CHOICES= [
        ('cod','Cash on Delivery'),
    ]
    PAYMENT_STATUS_CHOICES= [
        ('unpaid','Unpaid'),
        ('paid','Paid'),
        ('failed','Failed'),
    ]
    # Order Info
    order_number=models.CharField(max_length=20, unique=True,editable=False)
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    
    # Shipping Info
    full_name= models.CharField(max_length=200)
    phone=models.CharField(max_length=15)
    email=models.EmailField()
    address=models.TextField()
    city=models.CharField(max_length=100)
    province=models.CharField(max_length=50,choices=PROVINCE_CHOICES)
    
    # Pricing
    subtotal=models.DecimalField(max_digits=10,decimal_places=2)
    shipping_cost=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    total=models.DecimalField(max_digits=10,decimal_places=2)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES,default='cod')
    payment_status= models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES,default='unpaid')
    
    
    # Store 
    
    
    # Status
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    
    # Timestamps
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at= models.DateTimeField(auto_now=True)
    delivered_at = models.DateTimeField(null=True,blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD{timezone.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number}"
    

# ===================================
#   Order Items
# ===================================
class OrderItems(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    vendor_product = models.ForeignKey(VendorProduct,on_delete=models.SET_NULL,null=True)
    
    quantity=models.DecimalField(max_digits=10,decimal_places=2)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    
    def get_total(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.order.order_number} - {self.vendor_product.farmer_product.name}"
    

# ================================
#  Cart
# ================================
class Cart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    vendor_product=models.ForeignKey(VendorProduct,on_delete=models.CASCADE)
    quantity= models.DecimalField(max_digits=10,decimal_places=2,default=1)
    added_at=models.DateTimeField(auto_now_add=True)
    
    def get_total_price(self):
        return self.vendor_product.selling_price * self.quantity
    
    def __str__(self):
        return f"{self.user.first_name}'s cart-- {self.vendor_product.farmer_product.name}"


# ================================
#  Review and Rating
# ================================
class Review(models.Model):
    vendor_product=models.ForeignKey(VendorProduct,on_delete=models.CASCADE,related_name="reviews")
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    rating=models.PositiveSmallIntegerField(choices=[(i,i) for i in range(1,6) ])
    comment=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} - {self.vendor_product.farmer_product.name} {self.rating}"
    
    
# =============================
# Audit Log
# =============================
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('product_added', 'Product Added'),
        ('product_updated', 'Product Updated'),
        ('product_deleted', 'Product Deleted'),
        ('vendor_selected', 'Vendor Selected Product'),
        ('delivery_updated', 'Delivery Status Updated'),
        ('payout_requested', 'Payout Requested'),
        ('payout_approved', 'Payout Approved'),
        ('wallet_transaction', 'Wallet Transaction'),
        ('user_login', 'User Login'),
        ('order_placed', 'Order Placed'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    action=models.CharField(max_length=50,choices=ACTION_CHOICES)
    description=models.TextField()
    ip_address=models.GenericIPAddressField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} - {self.action}"
    
# =================================
#   Organizational Info 
# ================================
class Organization(models.Model):
    name=models.CharField(max_length=200)
    logo=models.ImageField(upload_to='org/')
    email=models.EmailField()
    phone=models.CharField(max_length=15)
    address=models.TextField()
    
    facebook=models.URLField(blank=True)
    instagram=models.URLField(blank=True)
    twitter=models.URLField(blank=True)
    
    def __str__(self):
        return self.name
    

# ==============================
#   Notification
# ==============================
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('order', 'Order Update'),
        ('product', 'Product Update'),
        ('payout', 'Payout Update'),
        ('selection', 'Product Selection'),
        ('delivery', 'Delivery Update'),
    ]
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    notification_type=models.CharField(max_length=20,choices=NOTIFICATION_TYPES)
    title= models.CharField(max_length=200)
    message=models.TextField()
    is_read= models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} - {self.title}"
    


# ================================
#  Signals
# ================================

@receiver(post_save, sender=User)
def create_admin_profile_and_role(sender,instance,created, **kwargs):
    """ Create UserProfile and UserRole for Admin """
    if created:
        UserProfile.objects.get_or_create(user=instance)
        if instance.is_superuser:
            UserRole.objects.get_or_create(user=instance,role='admin')

@receiver(post_save,sender=Farmer)
def create_farmer_wallet(sender,instance,created,**kwargs):
    """ Create wallet for new Farmer """
    if created:
        FarmerWallet.objects.get_or_create(farmer=instance)
        
@receiver(post_save,sender=Vendor)
def create_vendor_wallet(sender,instance,created,**kwargs):
    """ Create wallet for new vendor """
    if created:
        VendorWallet.objects.get_or_create(vendor=instance)
        

from django.db import transaction
@receiver(post_save,sender=Order)
def process_order_payment_split(sender,instance, **kwargs):
    """ Split payment when order is delivered """
    
    if hasattr(instance, '_payment_processed') and instance._payment_processed:
        return
    
    if instance.status == 'delivered'  and instance.payment_status == 'paid':
        commission_rate=CommissionRate.objects.first()
        if not commission_rate:
            return
        rate= commission_rate.rate/100
        half_rate=rate/2
        
        with transaction.atomic():
            for item in instance.items.all():
                vendor_product = item.vendor_product
                farmer_product=vendor_product.farmer_product
                
                total_amount=item.price * item.quantity
                
                farmer_commission,vendor_commission,total_commission=commission_rate.get_commission_amounts(total_amount)
                
                
                # Actual amounts
                farmer_base_amount=farmer_product.base_price * item.quantity
                farmer_final_amount=farmer_base_amount-farmer_commission
                
                vendor_base_amount=total_amount-farmer_base_amount
                vendor_final_amount=vendor_base_amount-vendor_commission
                
                # Credit Wallet
                farmer_wallet=farmer_product.farmer.farmer_wallet
                vendor_wallet=vendor_product.vendor.vendor_wallet
                admin_wallet,_=AdminWallet.objects.get_or_create(id=1)
                
                farmer_wallet.credit(farmer_final_amount)
                vendor_wallet.credit(vendor_final_amount)
                admin_wallet.credit(total_commission)
                
                #  Credit audit logs
                AuditLog.objects.create(user=instance.user,action='wallet_transaction',description=(
                        f"Order {instance.order_number} payment split: "
                        f"Farmer Rs.{farmer_final_amount}, "
                        f"Vendor Rs.{vendor_final_amount}, "
                        f"Farmer Commission Rs.{farmer_commission}, "
                        f"Vendor Commission Rs.{vendor_commission}"
                    ))
        #  Mark as processed
        instance._payment_processed = True
                

from django.db import transaction
from django.core.exceptions import ValidationError

@receiver(post_save,sender=VendorProduct)
def update_farmer_product_on_selection(sender,instance,created,**kwargs):
    """ Update farmer product when vendor selects it"""
    if created:
       
        
        # Use atomic transaction to prevent race condition
        with transaction.atomic():
            farmer_product=FarmerProduct.objects.select_for_update().get(id=instance.farmer_product.id)

            if instance.selected_quantity > farmer_product.available_quantity:
                raise ValidationError("Selected quantity ecceeds available quantity")
            
            # Update availabe quantity
            farmer_product.available_quantity -= instance.selected_quantity
            
            # Update delivery status is fully selected
            if farmer_product.available_quantity <= 0 :
                farmer_product.delivery_status = 'selected'
            
            farmer_product.save()
        
        # Create Notification for farmer
        Notification.objects.create(user=farmer_product.farmer.user,notification_type='selection',title='Product Selected by Vendor',
                                    message= f'{instance.vendor.shop_name} selected {instance.selected_quantity} kg of your {farmer_product.name}')
        #  Create Audit Log
        AuditLog.objects.create(user=instance.vendor.user,action='vendor_selected',description=f'Vendor {instance.vendor.shop_name} selected {instance.selected_quantity}kg of {farmer_product.name} from {farmer_product.farmer.farm_name}')




@receiver(post_save,sender=FarmerPayoutRequest)
def notify_payout_request(sender,instance,created,**kwargs):
    """ Notify admin  and farmer about payout request """
    if created :
        #  Notify all admin users
        admin_users=User.objects.filter(role__role='admin')
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type='payout',
                title='New Payout Request',
                message=f'{instance.farmer.farm_name} requested payout of Rs.{instance.requested_amount}'
            )
    
    #  Notify farmer when status is changes
    elif instance.status in ['approved','rejected','paid']:
        Notification.objects.create(user=instance.farmer.user,
                                    notification_type='payout',
                                    title=f'Payout Request {instance.get_status_display()}',
                                    message=f'Your payout request of Rs.{instance.requested_amount} has been  {instance.status}')


@receiver(post_save,sender=VendorPayoutRequest)
def notify_vendor_payout_request(sender,instance,created, **kwargs):
    """ Notify admin and vendor payout requests """
    if created:
        # Notify all admin users
        admin_users= User.objects.filter(role__role='admin')
        for admin in admin_users:
            Notification.objects.create(
                user=admin,
                notification_type='payout',
                title="New Vendor Payout Request",
                message=f'{instance.vendor.shop_name} requested payout of Rs.{instance.requested_amount}'
            )
    # Notify vendor when status changes
    elif instance.status in ['approved','rejected','paid']:
        Notification.objects.create(user=instance.vendor.user,
                                    notification_type='payout',
                                     title=f'Payout Request {instance.get_status_display()}',
                                    message=f'Your payout request of Rs.{instance.requested_amount} has been {instance.status}')
        


@receiver(post_save,sender=Order)
def notify_order_updates(sender,instance,**kwargs):
    "Notify customer about order status changes"
    if instance.user:
        status_messages={
            'processing':'Your order is being processed',
            'shipped':'Your order has been shipped',
            'delivered':'Your order has been delivered',
            'cancelled':'Your order has been cancelled',
        }
        
        if instance.status in status_messages:
            Notification.objects.create(
                user=instance.user,
                notification_type= 'order',
                title=f'Order {instance.order_number} Update',
                message=status_messages[instance.status]
            )
        
    
