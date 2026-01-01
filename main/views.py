from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'pages/home.html') 

def home1(request):
    return render(request, 'pages/home1.html') 

def about(request):
    return render(request, 'pages/about.html') 

def contact(request):
    return render(request, 'pages/contact.html') 

def farmers(request):
    return render(request, 'pages/farmers.html') 

def products_detail(request):
    return render(request, 'pages/products_detail.html') 

def products(request):
    return render(request, 'pages/products.html') 

def vendor(request):
    return render(request, 'pages/vendor.html') 

def cart(request):
    return render(request, 'pages/cart.html') 

def vender_detail(request):
    return render(request, 'pages/vender_detail.html') 
