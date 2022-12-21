from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.conf import settings

from django.contrib.auth.decorators import login_required
from user.decorators import user_active_required, betting_agency_required

from django.contrib import messages

from invoice.models import BettingAgencyInvoice, Invoice

from decimal import Decimal

import pytz

from io import BytesIO
import pandas as pd

# Create your views here.
@betting_agency_required
@user_active_required
@login_required(redirect_field_name=None)
def create_invoice(request):
    betting_agency_invoice = BettingAgencyInvoice(betting_agency=request.user.betting_agency)
    try:
        betting_agency_invoice.save()
        #
        _pending_draws = _seller_without_tickets = 0
        #
        for seller in request.user.user_set.all():
            total_sales = total_rewards = total_rewards_to_pay = total_commission = Decimal('0.00')
            invoice = Invoice(betting_agency=betting_agency_invoice)
            invoice.save()
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
                ticket.invoice = invoice
                ticket.save()
            # If seller does not have tickets sold to invoice
            if not total_sales:
                _seller_without_tickets += 1
                invoice.delete()
                continue
            #
            invoice.total_sales = total_sales
            invoice.total_rewards = total_rewards
            invoice.total_rewards_to_pay = total_rewards_to_pay
            invoice.total_commission = total_commission
            invoice.save()
        #
        if not betting_agency_invoice.invoice_set.exists(): raise
        #
        messages.success(request,
            'Se ha generado una factura (Tickets pendientes por sorteos: ' +str(_pending_draws) +', Vendedores sin tickets: ' +str(_seller_without_tickets) +').',
            extra_tags='alert-success'
        )
    except Exception as e:
        betting_agency_invoice.delete()
        messages.error(request, 'Error inesperado, la factura no fue generada.', extra_tags='alert-danger')
        return redirect('list_seller')
    return redirect(reverse('list_seller', kwargs= {'post_invoice': int(True)}))
#
@betting_agency_required
@user_active_required
@login_required(redirect_field_name=None)
def export_invoice(request, betting_agency_invoice=0):
    bet_agency_invoice = None
    if not betting_agency_invoice: bet_agency_invoice = BettingAgencyInvoice.objects.last()
    else: bet_agency_invoice = get_object_or_404(BettingAgencyInvoice, pk=betting_agency_invoice)
    #
    invoices_dict = [{
        'Fecha': invoice.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p'),
        'Vendedor': invoice.get_ticket_user_fullname(),
        'Total Ventas': invoice.total_sales,
        'Total A Pagar Ganadores': invoice.total_rewards,
        'Pendiente Por Pagar': invoice.total_rewards_to_pay,
        'Total Comisión': invoice.total_commission,
        'Total A Recaudar': invoice.total_sales - invoice.total_rewards - invoice.total_rewards_to_pay - invoice.total_commission,
    } for invoice in bet_agency_invoice.invoice_set.all()]
    #
    df_invoices = pd.DataFrame.from_dict(invoices_dict)
    with BytesIO() as b:
        #
        excel_writer = pd.ExcelWriter(b, engine='xlsxwriter')
        df_invoices.to_excel(excel_writer, sheet_name='Facturación')
        excel_writer.close()
        #
        response = HttpResponse(b.getvalue(), headers={
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename="' +str(bet_agency_invoice) +'.xlsx"',
        })
        return response