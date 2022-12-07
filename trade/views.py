from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from datetime import datetime, timedelta as td

from django.conf import settings

from lottery.models import Lottery, Pattern
from trade.models import Ticket, RowTicket
from draw.models import Draw

# Create your views here.
@csrf_protect
@login_required(redirect_field_name=None)
def sell_ticket(request, lottery):
    lottery = get_object_or_404(Lottery, pk=lottery)
    # Redirect if the lottery to select it does not belong to the betting_agency of the current user
    if not lottery in request.user.betting_agency.get_lotteries():
        messages.warning(request, 'No tiene permisos para realizar esta acción.', extra_tags='alert-warning')
        return redirect('index')
    # Current day draws filter
    available_draw = Draw.objects \
        .filter(schedule__lottery__exact=lottery) \
        .filter(schedule__day__exact=datetime.today().weekday())
    # Draws available given the current time
    # DRAW_CLOSE_MINUTES for secure bets/draws
    draw_list = list()
    _time = datetime.now().time()
    for draw in available_draw:
        if draw.schedule.turn > _time \
            and (td(hours=draw.schedule.turn.hour, minutes=draw.schedule.turn.minute, seconds=draw.schedule.turn.second) \
                - td(hours=_time.hour, minutes=_time.minute, seconds=_time.second)) > td(minutes=settings.DRAW_CLOSE_MINUTES):
            draw_list.append(draw)
    #
    if request.method == 'POST':
        ticket = Ticket(
            user=request.user,
            client=request.POST['client'])
        #
        try:
            # Resolves model validations
            ticket.save()
            for draw, pattern, bet_amount in \
                zip(request.POST.getlist('draw_list'), request.POST.getlist('pattern_list'), request.POST.getlist('bet_amount_list')):
                # Valid draw...
                _draw = Draw.objects.get(pk=draw)
                if (not _draw.schedule.turn > _time) \
                    or (td(hours=_draw.schedule.turn.hour, minutes=_draw.schedule.turn.minute, seconds=_draw.schedule.turn.second) \
                    - td(hours=_time.hour, minutes=_time.minute, seconds=_time.second)) < td(minutes=settings.DRAW_CLOSE_MINUTES):
                    messages.warning(request, '¡Atención! Revisa tu ticket, debido a un límite de horario un sorteo no fue incluido.', extra_tags='alert-warning')
                    continue
                _pattern = Pattern.objects.get(pk=pattern)
                #
                RowTicket(
                    ticket=ticket,
                    draw=_draw,
                    # IMPORTANT pattern_set was conveniently passed
                    icon=_pattern.icon,
                    bet_multiplier=_pattern.bet_multiplier,
                    bet_amount=int(bet_amount)
                ).save()
            messages.success(request, 'Un ticket ha sido generado.', extra_tags='alert-success')
            return redirect(reverse('ticket_status', kwargs= {'ticket': ticket.pk, 'post_sale': int(True)}))
        except Exception as e:
            ticket.delete()
            messages.error(request, 'Error inesperado, el ticket no fue generado.', extra_tags='alert-danger')
            return redirect(reverse('sell_ticket', kwargs={'lottery': lottery.pk}))
    #
    context = {
        'page_title': 'Venta de ticket',
        'lottery': lottery,
        'draw_list': draw_list,
        # IMPORTANT Pattern_set can be passed because a unique_together exists in the model
        'pattern_list': lottery.pattern_set.all()
    }
    return render(request, 'sell-ticket.html', context)
#
@login_required(redirect_field_name=None)
def ticket_status(request, ticket, post_sale=False):
    ticket = get_object_or_404(Ticket, pk=ticket)
    return render(request, 'ticket_status.html', {'ticket': ticket, 'post_sale': post_sale})
#
@login_required(redirect_field_name=None)
def invalidate_ticket(request, ticket):
    ticket = get_object_or_404(Ticket, pk=ticket)
    ticket.is_invalidated = True
    ticket.save()
    messages.warning(request, 'Ticket invalidado.', extra_tags='alert-warning')
    return redirect(reverse('ticket_status', kwargs= {'ticket': ticket.pk}))
#
@login_required(redirect_field_name=None)
def print_ticket(request, ticket):
    ticket = get_object_or_404(Ticket, pk=ticket)
    return render(request, 'to_print.html', context={'ticket': ticket})
#
@login_required(redirect_field_name=None)
def last_ticket(request):
    try:
        return render(request, 'ticket_status.html', {'ticket': request.user.ticket_set.last()})
    except:
        messages.warning(request, 'No ha vendido tickets aún.', extra_tags='alert-warning')
    return redirect('index')










# from django.http import HttpResponse
# from xhtml2pdf import pisa
# from django.template.loader import get_template
# from io import BytesIO

# @login_required(redirect_field_name=None)
# def print_ticket_copia(request, ticket):
#     ticket = get_object_or_404(Ticket, pk=ticket)
#     buffer = BytesIO()
#     template = get_template('to_print.html')
#     context = {
#         'ticket': ticket
#     }
#     html = template.render(context)
#     pisa_status = pisa.CreatePDF(html, dest=buffer)
#     if pisa_status.err:
#         messages.error(request, 'Error inesperado, el ticket no fue enviado a impresión', extra_tags='alert-danger')
#         return redirect(reverse('ticket_status', kwargs= {'ticket': ticket.pk}))
#     response = HttpResponse(buffer.getvalue(), headers={
#         'Content-Type': 'application/pdf',
#         # 'Content-Disposition': 'attachment; filename="ticket.pdf"',
#     })
#     return response