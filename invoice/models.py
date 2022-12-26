from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator
from user.models import User
from lottery.models import BettingAgency

from datetime import datetime
import pytz

from decimal import Decimal

# Create your models here.
class Commission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    percent = models.PositiveSmallIntegerField('Commission percentage', 
        validators=[MaxValueValidator(settings.MAX_COMMISSION_PERCENT)], default=0)
    sales_record = models.PositiveIntegerField('Sales record', default=2147483647)
    start_period = models.DateField(default=datetime.min.date())
    end_period = models.DateField(default=datetime.max.date())
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'commission'
    #
    def __str__(self): return '%s - Commission: %s%%' % (self.user.get_full_name(), self.percent)
    #
#
class Invoice(models.Model):
    betting_agency = models.ForeignKey(BettingAgency, on_delete=models.CASCADE)
    system_commission = models.PositiveSmallIntegerField('System Commission Percentage', default=0)
    was_paid = models.BooleanField('Was paid', default=False)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'invoice'
    #
    def get_total_sales(self):
        total_sales = Decimal('0.00')
        for row in self.rowinvoice_set.all():
            total_sales += row.total_sales
        return total_sales
    #
    def get_total_earnings(self):
        total_earning = Decimal('0.00')
        for row in self.rowinvoice_set.all():
            total_earning += row.total_sales - row.total_rewards - row.total_commission
        return total_earning
    #
    def get_total_to_pay_to_manager(self):
        _total = self.get_total_earnings() * Decimal(self.system_commission / 100)
        return _total if _total > Decimal('0.00') else Decimal('0.00')
    #
    def __str__(self):
        return '%s - Fecha: %s' % (
            self.betting_agency,
            self.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p')
        )
#
class RowInvoice(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    #
    total_sales = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_rewards = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_rewards_to_pay = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_commission = models.DecimalField('Total commission', max_digits=6, decimal_places=2, default=0)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'row_invoice'
        verbose_name = 'Row Invoice'
    #
    def get_ticket_user_fullname(self): return self.ticket_set.last().user.get_full_name()
#