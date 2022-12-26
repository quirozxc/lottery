from django.shortcuts import redirect
from django.contrib import messages

def bet_active_required(function):
    def wrap(request, *args, **kwargs):
        if not request.user.betting_agency.is_active:
            messages.warning(request,
                'Las operaciones para la agencia de lotería '
                + str(request.user.betting_agency)
                + ' se encuentran suspendidas. Comunicate con tu administrador.', extra_tags='alert-warning')
            return redirect('index')
        return function(request, *args, **kwargs)
    return wrap
#