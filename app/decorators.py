from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

# If the user is authenticated it will be redirected to the home otherwise continues the function
def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('app:homepage')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

# If the user does not have permissions the page is not shown
def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('Non sei autorizzato a vedere questa pagina.')

        return wrapper_func
    return decorator
