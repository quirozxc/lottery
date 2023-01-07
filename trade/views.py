from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.exceptions import PermissionDenied

from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from user.decorators import user_active_required, betting_manager_required
from lottery.decorators import bet_active_required

from datetime import datetime, timedelta as td
from django.utils import timezone

from django.conf import settings

from lottery.models import Lottery, Pattern
from trade.models import Ticket, RowTicket, WinningTicket
from draw.models import Draw

from decimal import Decimal

import pandas as pd
#
from PIL import Image, ImageDraw, ImageFont

from io import BytesIO
import base64

import pytz
#
def t_imagen(ticket):
    size_h = 250
    #
    ticket_str = str()
    ticket_str += str(ticket.user.betting_agency) +'\n'
    ticket_str += settings.TAX_PREFIX +' ' +ticket.user.betting_agency.tax_id +'\n'
    ticket_str += 'Ticket #' +ticket.get_readable_uuid() +'\n'
    ticket_str += ticket.get_lottery().name +'\n'
    ticket_str += 'Cliente: ' +str(ticket.client or settings.NOT_APPLY_LABEL) +'\n'
    ticket_str += 'Fecha: ' +ticket.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p') +'\n'
    ticket_str += 'Vendedor: ' +ticket.user.get_full_name() +'\n'
    ticket_str += '--------------------------------' +'\n'
    #
    for row in ticket.rowticket_set.all():
        ticket_str += row.draw.schedule.turn.strftime('%I:%M %p') +' - ' +row.icon.name +' - ' +ticket.user.betting_agency.get_currency_display() +' ' +str(row.bet_amount) +'\n'
        size_h += 30
    #
    ticket_str += '--------------------------------' +'\n'
    ticket_str += 'Total de apuesta: ' +ticket.user.betting_agency.get_currency_display() +' ' +str(ticket.get_total_bet_amount())
    size_h += 30
    #
    img = Image.new('L', (384, size_h), color=(255))
    path = settings.STATIC_ROOT / 'Roboto-Regular.ttf'
    fnt = ImageFont.truetype(str(path), 24)
    draw = ImageDraw.Draw(img)
    draw.multiline_text((10, 10), ticket_str, font=fnt, fill=(0))
    #
    # img.save('test.png')
    #
    with BytesIO() as buffered:
        img.save(buffered, format='PNG')
        img_str = base64.b64encode(buffered.getvalue())
        return img_str
    #
#
# Create your views here.
@csrf_protect
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def sell_ticket(request, lottery):
    lottery = get_object_or_404(Lottery, pk=lottery)
    # Redirect if the lottery to select it does not belong to the betting_agency of the current user
    if not lottery in request.user.betting_agency.get_lotteries(): raise PermissionDenied
    _time = datetime.now().time()
    #
    if request.method == 'POST':
        ticket = Ticket(
            user=request.user,
            client=request.POST.get('client') or None)
        #
        if request.user.commission_set.exists():
            ticket.user_commission_percent=request.user.commission_set.last().percent
        try:
            # Resolves model validations
            ticket.save()
            row_ticket_to_save = list()
            for draw, pattern, bet_amount in \
                zip(request.POST.getlist('draw_list'), request.POST.getlist('pattern_list'), request.POST.getlist('bet_amount_list')):
                # Valid draw...
                _draw = Draw.objects.get(pk=draw)
                if (not _draw.schedule.turn > _time) \
                    or (td(hours=_draw.schedule.turn.hour, minutes=_draw.schedule.turn.minute, seconds=_draw.schedule.turn.second) \
                    - td(hours=_time.hour, minutes=_time.minute, seconds=_time.second)) < td(minutes=settings.DRAW_CLOSE_MINUTES):
                    messages.warning(request, '¡Atención! Revisa el ticket, debido a un límite de horario un sorteo no fue incluido.', extra_tags='alert-warning')
                    continue
                _pattern = Pattern.objects.get(pk=pattern)
                # Validating in the backend the adding of a row_ticket with deactivated pattern
                if not _pattern.is_active: raise
                #
                row_ticket_to_save.append(
                    RowTicket(
                        ticket=ticket,
                        draw=_draw,
                        # IMPORTANT pattern_set was conveniently passed
                        icon=_pattern.icon,
                        bet_multiplier=_pattern.bet_multiplier,
                        bet_amount=int(bet_amount)
                    )
                )
            #
            RowTicket.objects.bulk_create(row_ticket_to_save)
            # Important if ticket has no rows
            if not ticket.rowticket_set.exists(): raise
            messages.success(request, 'Un ticket ha sido generado.', extra_tags='alert-success')
            return redirect(reverse('ticket', kwargs= {'ticket': ticket.pk, 'post_sale': int(True)}))
        except Exception as e:
            ticket.delete()
            messages.error(request, 'Error inesperado, el ticket no fue generado.', extra_tags='alert-danger')
            return redirect(reverse('sell_ticket', kwargs={'lottery': lottery.pk}))
    # Current day draws filter
    available_draw = Draw.objects \
        .filter(schedule__lottery=lottery) \
        .filter(date=datetime.today())
    # Draws available given the current time
    # DRAW_CLOSE_MINUTES for secure bets/draws
    draw_list = list()
    for draw in available_draw:
        if draw.schedule.turn > _time \
            and (td(hours=draw.schedule.turn.hour, minutes=draw.schedule.turn.minute, seconds=draw.schedule.turn.second) \
                - td(hours=_time.hour, minutes=_time.minute, seconds=_time.second)) > td(minutes=settings.DRAW_CLOSE_MINUTES):
            draw_list.append(draw)
    #
    context = {
        'page_title': 'Venta de ticket - ',
        'lottery': lottery,
        'draw_list': draw_list,
        # IMPORTANT Pattern_set can be passed because a unique_together exists in the model
        'pattern_list': lottery.pattern_set.filter(is_active=True)
    }
    return render(request, 'sell_ticket.html', context)
#
@user_active_required
@login_required(redirect_field_name=None)
def ticket(request, ticket, post_sale=False):
    ticket = get_object_or_404(Ticket, pk=ticket)
    if not ticket.user == request.user: raise PermissionDenied
    #
    ticket_imagen = t_imagen(ticket)
    ticket_imagen = ticket_imagen.decode('utf-8')
    #
    return render(request, 'ticket_details.html', {'page_title': 'Detalles de Ticket - ', 'ticket': ticket, 'post_sale': post_sale, 'ticket_imagen': ticket_imagen})
#
@user_active_required
@login_required(redirect_field_name=None)
def invalidate_ticket(request, ticket):
    ticket = get_object_or_404(Ticket, pk=ticket)
    # Cannot invalidate a ticket that the logged user did not sell.
    if not ticket.user == request.user: raise PermissionDenied
    # If exist a draw for any row of the ticket, then it cannot be invalidated
    for row_ticket in ticket.rowticket_set.all():
        if row_ticket.draw.drawresult_set.exists():
            messages.warning(request, 'Imposible invalidar este ticket.', extra_tags='alert-warning')
            return redirect(reverse('ticket', kwargs= {'ticket': ticket.pk}))
    ticket.is_invalidated = True
    ticket.save()
    messages.warning(request, 'Ticket invalidado.', extra_tags='alert-warning')
    return redirect(reverse('ticket', kwargs= {'ticket': ticket.pk}))
#
@user_active_required
@login_required(redirect_field_name=None)
def print_ticket(request, ticket):
    ticket = get_object_or_404(Ticket, pk=ticket)
    # Cannot print out a ticket that the logged user did not sell.
    if not ticket.user == request.user: raise PermissionDenied
    return render(request, 'to_print.html', context={'ticket': ticket})
#
@user_active_required
@login_required(redirect_field_name=None)
def last_ticket(request):
    try:
        ticket = request.user.ticket_set.last()
        #
        ticket_imagen = t_imagen(ticket)
        ticket_imagen = ticket_imagen.decode('utf-8')
        #
        return render(request, 'ticket_details.html', {'page_title': 'Detalles de Ticket - ', 'ticket': ticket, 'ticket_imagen': ticket_imagen})
    except:
        messages.warning(request, 'No ha vendido tickets aún.', extra_tags='alert-warning')
    return redirect('index')
#
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def search_ticket(request):
    raw_ticket = request.GET.get('ticket')
    # Get the different uuid of winning tickets for the logged user
    if int(raw_ticket) == 0: # Easter egg: with zero as parameter return all tickets...
        winner_row_ticket_found_list = WinningTicket.objects \
            .filter(row_ticket__ticket__user=request.user).values('uuid_ticket').distinct()
    else:
        winner_row_ticket_found_list = WinningTicket.objects \
            .filter(row_ticket__ticket__user=request.user) \
            .filter(uuid_ticket__icontains=raw_ticket).values('uuid_ticket').distinct()
    # 
    winner_ticket_list = list()
    for winner_ticket in winner_row_ticket_found_list:
        winner_ticket_list.append(WinningTicket.objects.filter(uuid_ticket=winner_ticket['uuid_ticket']).last())
    # 
    context = {
        'page_title': 'Resultado de Búsqueda - ',
        'raw_ticket': raw_ticket,
        'winner_ticket_list': winner_ticket_list,
    }
    return render(request, 'ticket_list.html', context)
#
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def winning_ticket(request, ticket):
    winner_ticket = get_object_or_404(Ticket, pk=ticket)
    #
    total_amount_to_pay = Decimal('0.00')
    for row_ticket in winner_ticket.rowticket_set.all():
        if row_ticket.is_a_winning_row():
            total_amount_to_pay += row_ticket.bet_amount_to_pay()
    #
    if not total_amount_to_pay:
        return redirect('index')
    #
    context = {
        'page_title': 'Detalles de Ticket Ganador - ',
        'winner_ticket': winner_ticket,
        'total_amount_to_pay': total_amount_to_pay,
    }
    return render(request, 'winner_ticket.html', context)
#
@bet_active_required
@user_active_required
@login_required(redirect_field_name=None)
def pay_ticket(request, winner_ticket):
    winner_ticket = get_object_or_404(Ticket, pk=winner_ticket)
    #
    if not winner_ticket.user == request.user: raise PermissionDenied
    #
    _check_is_a_winning_row = False
    row_ticket_rewarded = list()
    for row_ticket in winner_ticket.rowticket_set.all():
        if row_ticket.is_a_winning_row():
            _check_is_a_winning_row = True
            row_ticket.winningticket_set.all().delete()
            #
            row_ticket.was_rewarded = True
            row_ticket.payment = timezone.now()
            #
            row_ticket_rewarded.append(row_ticket)
    if _check_is_a_winning_row:
        RowTicket.objects.bulk_update(row_ticket_rewarded, ['was_rewarded', 'payment'])
        messages.success(request, 'Se ha registrado el pago de un ticket ganador.', extra_tags='alert-success')
    return redirect('index')
#
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def export_trade(request):
    if request.method == 'POST':
        from_date = datetime.strptime(request.POST.get('from_date'), '%Y-%m-%d')
        to_date = datetime.strptime(request.POST.get('to_date'), '%Y-%m-%d')
        to_date = datetime.combine(to_date, to_date.time().max)
        utc=pytz.UTC
        from_date = utc.localize(from_date)
        to_date = utc.localize(to_date)
        #
        if to_date > from_date:
            trade = [{
                'Fecha': row.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y'),
                'Hora': row.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%I:%M %p'),
                'Lotería': row.draw.schedule.lottery,
                'Vendedor': row.ticket.user.get_full_name(),
                'Cliente': row.ticket.get_client_or_notapply(),
                'Ticket': row.ticket.get_readable_uuid(),
                'Elección': row.icon.name,
                'Hora de Sorteo': row.draw.schedule.turn.strftime('%I:%M %p'),
                'Resultado de Sorteo': row.draw.drawresult_set.last().icon.name if row.draw.drawresult_set.last() else 'Sin Resultado Registrado',
                'Apuesta': row.bet_amount,
                'Multiplicador': row.bet_multiplier,
                'Premio': row.bet_amount_to_pay() if row.was_rewarded or row.is_a_winning_row() else Decimal('0.00'),
                'Pendiente': row.is_a_winning_row(),
                'Pagado': row.was_rewarded,
                'Fecha de Pago': row.payment.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p') if row.payment else settings.NOT_APPLY_LABEL,
                'Total del Ticket': row.ticket.get_total_bet_amount(),
                'Comisión del Ticket': row.ticket.user_commission_percent,
                'Facturación': row.ticket.row_invoice.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p') if row.ticket.row_invoice else 'Sin Factura Asignada',
            } for row in RowTicket.objects.filter(
                ticket__user__betting_agency=request.user.betting_agency,
                timestamp__gte=from_date,
                timestamp__lte=to_date,)]
            #
            if not trade:
                messages.warning(request, 'No hay datos en el rango de fecha seleccionado.', extra_tags='alert-warning')
                return redirect('list_seller')
            #
            df_invoices = pd.DataFrame.from_dict(trade)
            with BytesIO() as b:
                #
                excel_writer = pd.ExcelWriter(b, engine='xlsxwriter')
                df_invoices.to_excel(excel_writer, sheet_name='Venta de Ticket')
                excel_writer.close()
                #
                response = HttpResponse(b.getvalue(), headers={
                    'Content-Type': 'application/vnd.ms-excel',
                    'Content-Disposition': 'attachment; filename="Venta de ticket - ' +str(from_date.date()) +' - ' +str(to_date.date()) +'.xlsx"',
                })
                return response
            #
        else: messages.error(request, 'Error al generar el reporte, verifique el rango de fechas.', extra_tags='alert-danger')
    return redirect('list_seller')
#