from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse
from django.conf import settings

from django.contrib.auth.decorators import login_required
from user.decorators import user_active_required, betting_agency_required

from django.contrib import messages

from invoice.models import Invoice, RowInvoice
from trade.models import RowTicket

from decimal import Decimal

import pytz

from io import BytesIO
import pandas as pd

# Create your views here.
@betting_agency_required
@user_active_required
@login_required(redirect_field_name=None)
def create_invoice(request):
    invoice = Invoice(betting_agency=request.user.betting_agency)
    try:
        invoice.save()
        #
        _pending_draws = _seller_without_tickets = 0
        #
        for seller in request.user.user_set.all():
            total_sales = total_rewards = total_rewards_to_pay = total_commission = Decimal('0.00')
            row_invoice = RowInvoice(invoice=invoice)
            row_invoice.save()
            for ticket in seller.ticket_set.filter(invoice__isnull=True).filter(is_invalidated=False):
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
        if not invoice.rowinvoice_set.exists(): raise
        #
        messages.success(request,
            'Se ha generado una factura (Tickets pendientes por sorteos: ' +str(_pending_draws) +', Vendedores sin tickets: ' +str(_seller_without_tickets) +').',
            extra_tags='alert-success'
        )
    except Exception as e:
        invoice.delete()
        messages.error(request, 'Error inesperado, la factura no fue generada.', extra_tags='alert-danger')
        return redirect('list_seller')
    return redirect(reverse('list_seller', kwargs= {'post_invoice': int(True)}))
#
@betting_agency_required
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
        'Total A Recaudar': row.total_sales - row.total_rewards - row.total_rewards_to_pay - row.total_commission,
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
            row.total_sales - row.total_rewards - row.total_rewards_to_pay - row.total_commission
        )
    context = {
        'page_title': 'Lista de Facturas',
        'invoice_list': zip(row_invoice_list, total_collecting),
    }
    return render(request, 'user_invoice.html', context)
#
@betting_agency_required
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
        'Sorteo': row.draw,
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