from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.conf import settings

from django.contrib.auth.decorators import login_required
from user.decorators import user_active_required, betting_manager_required, system_manager_required

from django.views.decorators.csrf import csrf_protect

from django.contrib import messages

from invoice.models import Invoice, RowInvoice
from trade.models import RowTicket
from lottery.models import BettingAgency

from decimal import Decimal

from datetime import datetime
import pytz

from io import BytesIO
import pandas as pd

# Create your views here.
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def create_invoice(request):
    raise_exception_control = None
    # Daily invoicing validation
    if request.user.betting_agency.invoice_set.exists():
        if request.user.betting_agency.invoice_set.last().timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).date() == datetime.today().date():
            messages.warning(request, 'Ya existe registrada una factura para el día de hoy.', extra_tags='alert-warning')
            return redirect('list_seller')
        #
    #
    invoice = Invoice(
        betting_agency=request.user.betting_agency,
        system_commission=request.user.betting_agency.system_commission,
    )
    try:
        invoice.save()
        #
        _pending_draws = _seller_without_tickets = 0
        #
        for seller in request.user.user_set.all():
            total_sales = total_rewards = total_rewards_to_pay = total_commission = Decimal('0.00')
            row_invoice = RowInvoice(invoice=invoice)
            row_invoice.save()
            for ticket in seller.ticket_set.filter(row_invoice__isnull=True).filter(is_invalidated=False):
                # If has pending draws, it is not included for invoicing
                if ticket.has_pending_draws():
                    _pending_draws += 1
                    continue
                #
                _ticket_total_amount = ticket.get_total_bet_amount()
                #
                total_sales += _ticket_total_amount
                total_rewards += ticket.get_total_reward()
                total_rewards_to_pay += ticket.get_total_reward_pending_to_pay()
                total_commission += _ticket_total_amount * Decimal(ticket.user_commission_percent / 100)
                #
                ticket.row_invoice = row_invoice
                ticket.save()
            # If seller does not have tickets sold to invoice
            if not total_sales:
                _seller_without_tickets += 1
                row_invoice.delete()
                continue
            #
            row_invoice.total_sales = total_sales
            row_invoice.total_rewards = total_rewards
            row_invoice.total_rewards_to_pay = total_rewards_to_pay
            row_invoice.total_commission = total_commission
            row_invoice.save()
        #
        if not invoice.rowinvoice_set.exists():
            raise_exception_control = True
            raise
        #
        messages.success(request,
            'Se ha generado una factura (Tickets pendientes por sorteos: ' +str(_pending_draws) +', Vendedores sin tickets: ' +str(_seller_without_tickets) +').',
            extra_tags='alert-success'
        )
    except Exception as e:
        invoice.delete()
        if raise_exception_control: messages.warning(request, 'No hay datos disponibles para facturar.', extra_tags='alert-warning')
        else: messages.error(request, 'Error inesperado, la factura no fue generada.', extra_tags='alert-danger')
        return redirect('list_seller')
    return redirect(reverse('list_seller', kwargs= {'post_invoice': int(True)}))
#
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def export_invoice(request, invoice=0):
    _invoice = None
    if not invoice: _invoice = Invoice.objects.last()
    else: _invoice = get_object_or_404(Invoice, pk=invoice)
    invoice = _invoice
    #
    row_invoices_dict = [{
        'Fecha': row.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p'),
        'Vendedor': row.get_ticket_user_fullname(),
        'Total Ventas': row.total_sales,
        'Total A Pagar Ganadores': row.total_rewards,
        'Pendiente Por Pagar': row.total_rewards_to_pay,
        'Total Comisión': row.total_commission,
        'Total A Recaudar': row.total_sales - row.total_rewards - row.total_commission,
    } for row in invoice.rowinvoice_set.all()]
    #
    df_row_invoices = pd.DataFrame.from_dict(row_invoices_dict)
    with BytesIO() as b:
        #
        excel_writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df_row_invoices.to_excel(excel_writer, sheet_name='Facturación')
        excel_writer.close()
        #
        response = HttpResponse(b.getvalue(), headers={
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename="' +str(invoice) +'.xlsx"',
        })
        return response
    #
#
@user_active_required
@login_required(redirect_field_name=None)
def user_invoice_list(request):
    row_invoice_list = RowInvoice.objects.filter(ticket__user=request.user).distinct().order_by('-id')
    total_collecting = list()
    for row in row_invoice_list:
        total_collecting.append(
            row.total_sales - row.total_rewards - row.total_commission
        )
    context = {
        'page_title': 'Lista de Facturas - ',
        'invoice_list': zip(row_invoice_list, total_collecting),
    }
    return render(request, 'user_invoice.html', context)
#
@betting_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def export_matrix(request, invoice=0):
    _invoice = None
    if not invoice: _invoice = Invoice.objects.last()
    else: _invoice = get_object_or_404(Invoice, pk=invoice)
    invoice = _invoice
    #
    matrix = [{
        'Fecha': row.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p'),
        'Lotería': row.draw.schedule.lottery,
        'Vendedor': row.ticket.user.get_full_name(),
        'Cliente': row.ticket.get_client_or_notapply(),
        'Ticket': row.ticket.get_readable_uuid(),
        'Elección': row.icon.name,
        'Hora-Sorteo': row.draw.schedule.turn.strftime('%I:%M %p'),
        'Resultado': row.draw.drawresult_set.last().icon.name,
        'Apuesta': row.bet_amount,
        'Multiplicador': row.bet_multiplier,
        'Comisión': row.ticket.user_commission_percent,
        'Pagado': row.was_rewarded,
        'Pendiente': row.is_a_winning_row(),
        'Total-Apuesta': row.ticket.get_total_bet_amount(),
        'Premio': row.bet_amount_to_pay() if row.was_rewarded or row.is_a_winning_row() else Decimal('0.00')
    } for row in RowTicket.objects.filter(ticket__row_invoice__invoice=invoice)]
    #
    df_invoices = pd.DataFrame.from_dict(matrix)
    with BytesIO() as b:
        #
        excel_writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df_invoices.to_excel(excel_writer, sheet_name='Matriz')
        excel_writer.close()
        #
        response = HttpResponse(b.getvalue(), headers={
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename="Matriz - ' +str(invoice) +'.xlsx"',
        })
        return response
    #
#
@csrf_protect
@system_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def management(request, betting_agency=None):
    if betting_agency: betting_agency = get_object_or_404(BettingAgency, pk=betting_agency)
    if request.method == 'POST' and request.POST.get('betting_agency').isdigit():
        betting_agency = get_object_or_404(BettingAgency, pk=request.POST.get('betting_agency'))
    #
    context = {
        'page_title': 'Administración - ',
        'betting_agency_list': BettingAgency.objects.all(),
        'betting_agency': betting_agency,
    }
    if betting_agency: context.update({'invoice_list': betting_agency.invoice_set.all().order_by('-id')})
    #
    return render(request, 'management.html', context)
#
@csrf_protect
@system_manager_required
@user_active_required
@login_required(redirect_field_name=None)
def pay_to_manager(request):
    if request.method == 'POST':
        _changes = None
        bet_agency_checked = list(map(int, request.POST.getlist('invoice')))
        bet_agency_invoices = None
        try: # Without invoices...
            bet_agency_invoices = Invoice.objects.filter(betting_agency=request.POST.get('betting_agency'))
            if not bet_agency_invoices.exists(): raise
        except:
            messages.error(request, 'Error inesperado, no se registro nigún cambio.', extra_tags='alert-danger')
            return redirect('management')
        #
        for invoice in bet_agency_invoices:
            if invoice.pk in bet_agency_checked:
                if invoice.was_paid == False:
                    invoice.was_paid = True
                    _changes = True
            else:
                if invoice.was_paid == True:
                    invoice.was_paid = False
                    _changes = True
                #
            invoice.save()
            #
        if _changes: messages.success(request, 'Se actualizaron los pagos de facturas.', extra_tags='alert-success')
        else: messages.warning(request, 'No se guardó ningún cambio.', extra_tags='alert-warning')
    return redirect(reverse('management', kwargs={'betting_agency': request.POST.get('betting_agency')}))