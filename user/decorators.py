from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages

def user_active_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_active:
            messages.warning(request, 'Tu cuenta se encuentra suspendida. Comunicate con tu administrador.', extra_tags='alert-warning')
            return redirect('logout')
        return function(request, *args, **kwargs)
    return wrap
#
def banker_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_banker: raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap
#
def betting_agency_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.is_betting_agency_staff: raise PermissionDenied
        return function(request, *args, **kwargs)
    return wrap