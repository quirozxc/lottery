from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from user.decorators import user_active_required, system_manager_required
from .forms import BettingAgencyEditForm
from lottery.models import BettingAgency

# Create your views here.
@system_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def betting_agency_list(request):
    context = {
        'page_title': 'Lista de Agencias de Lotería',
        'betting_agency_list': BettingAgency.objects.all(),
    }
    return render(request, 'betting_agency_list.html', context)
#
@system_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def edit_betting_agency(request, betting_agency):
    betting_agency = get_object_or_404(BettingAgency, pk=betting_agency)
    if request.method == 'POST':
        form = BettingAgencyEditForm(request.POST, instance=betting_agency)
        if form.is_valid():
            form.save()
            messages.success(request, 'La Agencia de Lotería ha sido actualizada.', extra_tags='alert-success')
            return redirect('betting_agency_list')
        else: print(form.errors)
    context = {
        'page_title': 'Actualizar Agencia de Lotería',
        'form': BettingAgencyEditForm(instance=betting_agency),
        'betting_agency': betting_agency,
    }
    return render(request, 'edit_betting_agency.html', context)