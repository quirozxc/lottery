from django.db import models
from django.contrib.auth.models import AbstractUser
from lottery.models import BettingAgency

# Create your models here.

class User(AbstractUser):
    banker = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)
    betting_agency = models.ForeignKey(BettingAgency, on_delete=models.CASCADE, null=True, blank=True)
    is_banker = models.BooleanField('Can create seller\'s', default=False)
    is_betting_agency_staff = models.BooleanField('Can register a lottery result', default=False)
    #
    class Meta:
        db_table = 'user'