from django.shortcuts import render

# Create your views here.

def farmer_dashboard(request):
    return render(request,'farmer/pages/dashboard.html')