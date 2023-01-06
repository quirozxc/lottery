from django.db import models
from lottery.models import Icon
from draw.models import Draw, DrawResult
from user.models import User
from invoice.models import RowInvoice

from django.conf import settings
from django.core.validators import MaxValueValidator

from decimal import Decimal
import uuid

from django.utils import timezone

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.PositiveIntegerField('DNI', null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    was_printed = models.BooleanField('Print control', default=False)
    is_invalidated = models.BooleanField('Invalidation control', default=False)
    #
    user_commission_percent = models.PositiveSmallIntegerField('Commission percentage', 
        validators=[MaxValueValidator(settings.MAX_COMMISSION_PERCENT)], default=0)
    row_invoice = models.ForeignKey(RowInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'ticket'
    #
    def has_pending_draws(self):
        if self.rowticket_set.exists():
            for row in self.rowticket_set.all():
                if not row.draw.drawresult_set.exists():
                    return True
        return False

    #
    def get_total_bet_amount(self):
        t_amount = Decimal('0.00')
        if self.rowticket_set.exists():
            for row in self.rowticket_set.all():
                t_amount += row.bet_amount
        return t_amount
    #
    def get_total_reward(self):
        t_reward = Decimal('0.00')
        if self.rowticket_set.exists():
            for row in self.rowticket_set.all():
                if row.is_a_winning_row() or row.was_rewarded:
                    t_reward += row.bet_amount_to_pay()
        return t_reward
    #
    def get_total_reward_pending_to_pay(self):
        t_pending_reward = Decimal('0.00')
        if self.rowticket_set.exists():
            for row in self.rowticket_set.all():
                if row.is_a_winning_row():
                    t_pending_reward += row.bet_amount_to_pay()
        return t_pending_reward
    #
    def get_lottery(self): return self.rowticket_set.last().draw.schedule.lottery
    #
    def get_readable_uuid(self): return str(self.uuid.int)[-10:]
    #
    def get_client_or_notapply(self): return self.client if self.client else settings.NOT_APPLY_LABEL
    #
    def __str__(self): return 'Ticket Nº %d - UUID Readable: #%s' % (self.pk, self.get_readable_uuid())
#
class RowTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    bet_multiplier = models.PositiveIntegerField('Bet multiplier')
    bet_amount = models.DecimalField('Bet amount', max_digits=6, decimal_places=2)
    was_rewarded = models.BooleanField('Was rewarded', default=False)
    payment = models.DateTimeField('Payment timestamp', null=True, blank=True)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'row_ticket'
        verbose_name = 'Row Ticket'
    #
    def clean(self):
        if self.was_rewarded == True: self.payment = timezone.now()
        return super().clean()
    #
    def bet_amount_to_pay(self): return self.bet_amount *self.bet_multiplier
    #
    def is_a_winning_row(self): return self.winningticket_set.exists()
    #
    def __str__(self): return '%s - %s - %s' % (self.ticket, self.draw, self.icon.name) 
#
class WinningTicket(models.Model):
    row_ticket = models.ForeignKey(RowTicket, on_delete=models.CASCADE)
    draw_result = models.ForeignKey(DrawResult, on_delete=models.CASCADE)
    uuid_ticket = models.CharField('Readable uuid of ticket', max_length=10, editable=False)
    #
    class Meta:
        db_table = 'winning_ticket'
        verbose_name = 'Winning Ticket'
    #
    def __str__(self): return '%s' % (self.row_ticket)