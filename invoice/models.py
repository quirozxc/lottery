from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator
from user.models import User
from lottery.models import BettingAgency

from datetime import datetime
import pytz

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
class BettingAgencyInvoice(models.Model):
    betting_agency = models.ForeignKey(BettingAgency, on_delete=models.CASCADE)
    was_paid = models.BooleanField('Was paid', default=False)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'betting_agency_invoice'
        verbose_name = 'Betting Agency - Invoice'
    #
    def __str__(self):
        return '%s - Fecha: %s' % (
            self.betting_agency,
            self.timestamp.astimezone(pytz.timezone(settings.TIME_ZONE)).strftime('%d/%m/%Y - %I:%M %p')
        )
#
class Invoice(models.Model):
    betting_agency = models.ForeignKey(BettingAgencyInvoice, on_delete=models.CASCADE)
    #
    total_sales = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_rewards = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_rewards_to_pay = models.DecimalField('Total sales', max_digits=6, decimal_places=2, default=0)
    total_commission = models.DecimalField('Total commission', max_digits=6, decimal_places=2, default=0)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'invoice'
    #
    def get_ticket_user_fullname(self): return self.ticket_set.last().user.get_full_name()
#