from django.shortcuts import render, get_object_or_404, redirect

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from django.core.exceptions import PermissionDenied

from user.decorators import user_active_required, system_manager_required, betting_manager_required
from .forms import BettingAgencyEditForm
from lottery.models import BettingAgency, Pattern, Lottery

# Create your views here.
@system_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def betting_agency_list(request):
    context = {
        'page_title': 'Lista de Agencias - ',
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
            messages.success(request, 'La agencia de lotería ha sido actualizada.', extra_tags='alert-success')
            return redirect('betting_agency_list')
        else: print(form.errors)
    context = {
        'page_title': 'Actualizar Agencia - ',
        'form': BettingAgencyEditForm(instance=betting_agency),
        'betting_agency': betting_agency,
    }
    return render(request, 'edit_betting_agency.html', context)
#
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def edit_pattern(request, lottery, betting_agency):
    betting_agency = get_object_or_404(BettingAgency, pk=betting_agency)
    lottery = get_object_or_404(Lottery, pk=lottery)
    if not request.user.betting_agency == betting_agency: raise PermissionDenied
    #
    pattern_set = Pattern.objects.filter(betting_agency=betting_agency).filter(lottery=lottery)
    #
    if request.method == 'POST':
        _changes = None
        pattern_checked = list(map(int, request.POST.getlist('pattern')))
        #
        pattern_to_update = list()
        for pattern in pattern_set:
            if pattern.pk in pattern_checked:
                if pattern.is_active == False:
                    pattern.is_active = True
                    pattern_to_update.append(pattern)
                    _changes = True
            else:
                if pattern.is_active == True:
                    pattern.is_active = False
                    pattern_to_update.append(pattern)
                    _changes = True
                #
            #
        #
        Pattern.objects.bulk_update(pattern_to_update, ['is_active'])
        #
        if _changes: messages.success(request, 'Se actualizaron los datos de la lotería.', extra_tags='alert-success')
        else: messages.warning(request, 'No se guardó ningún cambio.', extra_tags='alert-warning')
    #
    context={
        'page_title': 'Actualizar Lotería - ',
        'lottery': lottery,
        'pattern_set': pattern_set,
    }
    return render(request, 'edit_pattern.html', context)