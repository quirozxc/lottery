from django.db import models
from lottery.models import Icon
from draw.models import Draw
from user.models import User

# Create your models here.
class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.PositiveIntegerField('DNI')
    unique_number = models.PositiveIntegerField('Unique control number', unique=True, null=True, blank=True)
    was_printed = models.BooleanField('Print control')
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'ticket'
    #
    def save(self, *args, **kwargs):
        super(Ticket, self).save(*args, **kwargs)
        # self.unique_number ...
        print('DEVs working...')
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