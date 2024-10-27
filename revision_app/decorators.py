from django.http import HttpResponse
from django.shortcuts import redirect

# decorator that stops an authenticated user from viewing the login
# decorator is a function that takes another function in as a parameter and, 
# allows us to dd additional functionalities before the original function is called
def unauthenicated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            
            if group in allowed_roles:
            # print("Working", allowed_roles)
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("You are not authorized to view this page")
        return wrapper_func
    return decorator

def admin_only(view_func):
    def wrapper_func(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name

        if group == "sales_person":
            return redirect("sales")
        
        if group == 'admin':
            return view_func(request, *args, **kwargs)
    return wrapper_func