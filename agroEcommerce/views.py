from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import logout


from .models import UserProfile,UserRole





def login_page(request):
    if request.method =="POST":
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=User.objects.get(email=email)
            if user.check_password(password):
                login(request,user)
                messages.success(request,'Logged in successfully!')
                try:
                    if user.role.role == 'admin':
                        return redirect('admin_dashboard_page')
                    elif user.role.role == 'vendor':
                        return redirect('vendor_dashboard_page')
                    elif user.role.role == 'farmer':
                        return redirect('farmer_dashboard_page')
                except Exception as e:
                    messages.error(request,f'Error {str(e)}')
                    return redirect('login_page')
        except User.DoesNotExist:
            messages.error(request,'Invalid email or password')
            return redirect('login_page')
    
    return render(request,'pages/login.html')

def logout_page(request):
    logout(request)
    messages.success(request,'Logged out successfully!')
    return redirect('login_page')



# Create your views here.
def home(request):
    return render(request, 'website/pages/home.html') 

def home1(request):
    return render(request, 'website/pages/home1.html') 

def about(request):
    return render(request, 'website/pages/about.html') 

def contact(request):
    return render(request, 'website/pages/contact.html') 

def farmers(request):
    return render(request, 'website/pages/farmers.html') 

def products_detail(request):
    return render(request, 'website/pages/products_detail.html') 

def products(request):
    return render(request, 'website/pages/products.html') 

def vendor(request):
    return render(request, 'website/pages/vendor.html') 

def cart(request):
    return render(request, 'website/pages/cart.html') 

def vendor_detail(request):
    return render(request, 'website/pages/vendor_detail.html') 

def checkout(request):
    return render(request, 'website/pages/checkout.html') 

def vegetables(request):
    return render(request, 'website/pages/vegetables.html') 

def farmers_detail(request):
    return render(request, 'website/pages/farmers_detail.html') 

def order_confirmation(request):
    return render(request, 'website/pages/order_confirmation.html') 

def faq(request):
    return render(request, 'website/pages/faq.html')
def privacy_policy(request):
    return render(request, 'website/pages/privacy_policy.html')

def term_of_services(request):
    return render(request, 'website/pages/term_of_services.html')

def refund_and_return(request):
    return render(request, 'website/pages/refund_and_return.html')