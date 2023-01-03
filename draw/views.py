from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from user.decorators import user_active_required, betting_manager_required
from lottery.decorators import bet_active_required

from datetime import datetime

from lottery.models import Lottery, Icon
from trade.models import RowTicket, WinningTicket
from draw.models import Draw, DrawResult

# Create your views here.
@betting_manager_required
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def confirm_draw(request, draw_result):
    if not request.META.get('HTTP_REFERER'): return redirect('index')
    #
    draw_result = get_object_or_404(DrawResult, pk=draw_result)
    context = {'page_title': 'Confirmación de Resultado - ', 'draw_result': draw_result}
    return render(request, 'confirm_draw.html', context)
#
@csrf_protect
@betting_manager_required
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def draw_register(request, lottery):
    lottery = get_object_or_404(Lottery, pk=lottery)
    available_draw = Draw.objects \
        .filter(schedule__lottery=lottery) \
        .filter(date=datetime.today()) \
        .filter(drawresult__isnull=True)
    #
    if request.method == 'POST':
        draw=Draw.objects.get(pk=request.POST.get('draw_to_register'))
        icon=Icon.objects.get(pk=request.POST.get('icon'))
        # If user returns from browser option...
        if draw.drawresult_set.exists(): draw.drawresult_set.last().delete()
        #
        draw_result = DrawResult(
            draw=draw,
            icon=icon
        )
        draw_result.save()
        # Update row_ticket winners
        winners = RowTicket.objects.filter(draw=draw).filter(icon=icon).filter(ticket__is_invalidated=False)
        winner_ticket = list()
        for winner_ticket_row in winners:
            winner_ticket.append(
                WinningTicket(
                    row_ticket=winner_ticket_row,
                    draw_result=draw_result,
                    uuid_ticket=winner_ticket_row.ticket.get_readable_uuid()
                )
            )
        WinningTicket.objects.bulk_create(winner_ticket)
        #
        messages.success(request, 'Se ha registrado un resultado (Ganadores: ' +str(winners.count()) +').', extra_tags='alert-success')
        return redirect(reverse('confirm_draw', kwargs={'draw_result': draw_result.pk}))
    # Draw that have been made validating per hour
    _time = datetime.now().time()
    draw_to_register_list = list()
    for draw in available_draw:
        if draw.schedule.turn < _time:
            draw_to_register_list.append(draw)
    # 
    context = {
        'page_title': 'Registro de Resultado - ',
        'lottery': lottery,
        'draw_to_register_list': draw_to_register_list,
        # IMPORTANT Pattern_set can be passed because a unique_together exists in the model
        'pattern_list': lottery.pattern_set.all()
    }
    return render(request, 'draw_register.html', context)
#
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def delete_draw(request, draw_result):
    if not request.META.get('HTTP_REFERER'): return redirect('index')
    #
    draw_result = get_object_or_404(DrawResult, pk=draw_result)
    lottery = draw_result.draw.schedule.lottery
    draw_result.delete()
    messages.warning(request, 'Se ha eliminado el resultado.', extra_tags='alert-warning')
    # messages.success(request, 'Puede volver a registrar el resultado correcto.', extra_tags='alert-success')
    return redirect(reverse('draw_register', kwargs={'lottery': lottery.pk}))