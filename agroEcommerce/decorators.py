from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args,**kwargs):
        if not request.user.is_authenticated:
            messages.error(request,'Please Login')
            return redirect('login_page')
        
        if not request.user.role.role == 'admin':
            messages.error(request,'Not Authorized access')
            return redirect('login_page')
        
        return view_func(request,*args,**kwargs)
    return  wrapper



            