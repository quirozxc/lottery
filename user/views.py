from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import LoginForm, SellerCreateForm, SellerChangeForm
from .decorators import banker_required, user_active_required
from .models import User

# Create your views here.
def login(request):
    if request.user.is_authenticated: return redirect('index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                _login(request, user)
                # Inactive user verification - Redirection...
                if not user.is_active:
                    messages.warning(request, 'Tu cuenta se encuentra suspendida. Comunicate con tu administrador.', extra_tags='alert-warning')
                    return logout(request)
                return redirect('index')
            else: messages.warning(request, '¡Usuario y contraseña no coinciden!', extra_tags='alert-warning')
        else: messages.error(request, form.errors.as_text(), extra_tags='alert-danger')
    context = {
        'page_title': 'Iniciar Sesión',
        'form': LoginForm()
    }
    return render(request, 'login.html', context)
#
@login_required(redirect_field_name=None)
def index(request):
    if request.user.is_superuser: return redirect('/admin')
    return render(request, 'index.html', context={'page_title': 'Sistema de Lotería',})
#
@login_required(redirect_field_name=None)
def logout(request):
    _logout(request)
    return redirect('login')
#
@login_required(redirect_field_name=None)
def password_change(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, '¡Cambiaste la contraseña con exito!', extra_tags='alert-success')
            return redirect('index')
        else: messages.error(request, form.errors.as_text(), extra_tags='alert-danger')
    context = {
        'page_title': 'Cambio de Contraseña',
        'form': PasswordChangeForm(user=request.user)
    }
    return render(request, 'password_change.html', context)
#
@banker_required
@user_active_required
@login_required(redirect_field_name=None)
def create_seller(request):
    if request.method == 'POST':
        form = SellerCreateForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=False)
            # Indicator of sellers belonging to the banker/betting agency
            seller.banker = request.user
            seller.betting_agency = request.user.betting_agency
            seller.save()
            #
            messages.success(request, '¡Nuevo vendedor registrado!', extra_tags='alert-success')
            return redirect('list_seller')
        else: messages.error(request, form.errors.as_text(), extra_tags='alert-danger')
    context = {
        'page_title': 'Registrar Vendedor',
        'form': SellerCreateForm(),
    }
    return render(request, 'create_seller.html', context)
#
@login_required(redirect_field_name=None)
@banker_required
def list_seller(request):
    seller_list = User.objects.filter(banker__exact=request.user)
    context = {
        'seller_list': seller_list
    }
    return render(request, 'seller_list.html', context)
#
@banker_required
@user_active_required
@login_required(redirect_field_name=None)
def change_seller(request, seller):
    seller = get_object_or_404(User, pk=seller)
    if request.method == 'POST':
        form = SellerChangeForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El vendedor ha sido actualizado!', extra_tags='alert-success')
            return redirect('list_seller')
        else: messages.error(request, form.errors.as_text(), extra_tags='alert-danger')
    context = {
        'page_title': 'Actualizar Vendedor',
        'form': SellerChangeForm(instance=seller),
        'seller': seller,
    }
    return render(request, 'change_seller.html', context)
#
@banker_required
@user_active_required
@login_required(redirect_field_name=None)
def reset_password(request, seller):
    seller = get_object_or_404(User, pk=seller)
    if seller.banker == request.user:
        seller.set_password('12345678')
        seller.save()
        messages.success(request, 'La contraseña para: "'+seller.username +'", ha sido reseteada.', extra_tags='alert-success')
        return redirect('list_seller')
    else:
        messages.warning(request, 'No tiene permisos para realizar esta acción.', extra_tags='alert-warning')
    return redirect('index')