from django.db import models
from lottery.models import Icon
from draw.models import Draw
from user.models import User
from draw.models import DrawResult

from decimal import Decimal
import uuid

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.PositiveIntegerField('DNI', null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    was_printed = models.BooleanField('Print control', default=False)
    is_invalidated = models.BooleanField('Invalidation control', default=False)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'ticket'
    #
    def get_total_bet_amount(self):
        t_amount = Decimal('0.00')
        if self.rowticket_set.exists():
            for row in self.rowticket_set.all():
                t_amount += row.bet_amount
        return t_amount
    #
    def get_lottery(self): return self.rowticket_set.first().draw.schedule.lottery
    #
    def get_readable_uuid(self): return str(self.uuid.int)[-10:]
    #
    def __str__(self): return 'ticket #%d - serial: %s' % (self.pk, self.get_readable_uuid())
#
class RowTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    bet_multiplier = models.PositiveIntegerField('Bet multiplier')
    bet_amount = models.DecimalField('Bet amount', max_digits=6, decimal_places=2)
    was_rewarded = models.BooleanField('Is winner', default=False)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'row_ticket'
    #
    def bet_amount_to_pay(self): return self.bet_amount *self.bet_multiplier
#
class WinningTicket(models.Model):
    row_ticket = models.ForeignKey(RowTicket, on_delete=models.CASCADE)
    draw_result = models.ForeignKey(DrawResult, on_delete=models.CASCADE)
    uuid_ticket = models.CharField('Readable uuid of ticket', max_length=10)
    #
    class Meta:
        db_table = 'winning_ticket'