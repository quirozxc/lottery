from django.db import models
from django.contrib.auth.models import AbstractUser
from lottery.models import BettingAgency

# Create your models here.

class User(AbstractUser):
    banker = models.ForeignKey('self', on_delete=models.RESTRICT, null=True, blank=True)
    betting_agency = models.ForeignKey(BettingAgency, on_delete=models.CASCADE, null=True, blank=True)
    is_banker = models.BooleanField('Can create sellers', default=False)
    is_betting_agency_staff = models.BooleanField('Can register a lottery result', default=False)
    #
    is_system_manager = models.BooleanField('Lottery System Administrator', default=False)
    #
    class Meta:
        db_table = 'user'
    #
    def get_full_name(self): return '%s %s' % (self.first_name, self.last_name)
    #
    def clean(self):
        self.username = self.username.lower()
        self.first_name = self.first_name.title()
        self.last_name = self.last_name.title()
        return super().clean()