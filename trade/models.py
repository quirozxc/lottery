from django.db import models
from lottery.models import Icon
from draw.models import Draw
from user.models import User

import uuid

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.PositiveIntegerField('DNI')
    unique_number = models.PositiveIntegerField('Unique control number', null=True, blank=True)
    was_printed = models.BooleanField('Print control', default=False)
    is_invalidated = models.BooleanField('Invalidation control', default=False)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'ticket'
    #
    def save(self, *args, **kwargs):
        self.unique_number = uuid.uuid4().int & (1<<31)-1
        super(Ticket, self).save(*args, **kwargs)
    #
    def __str__(self): return 'ticket #%d - serial: %d' % (self.pk, self.unique_number)
#
class RowTicket(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    bet_multiplier = models.PositiveIntegerField('Bet multiplier')
    bet_amount = models.DecimalField('Bet amount', max_digits=6, decimal_places=2)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'row_ticket'
    #