from django.db import models
from django.conf import settings

# Create your models here.
class Lottery(models.Model):
    name = models.CharField('Name of lottery', max_length=150)
    picture = models.ImageField('Logo', upload_to='lottery', null=True, blank=True)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'lottery'
    #
    def __str__(self): return self.name
#
class Schedule(models.Model):
    DAYS = (
        ('0', 'Lunes'),
        ('1', 'Martes'),
        ('2', 'Miercoles'),
        ('3', 'Jueves'),
        ('4', 'Viernes'),
        ('5', 'Sábado'),
        ('6', 'Domingo'),
    )
    #
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE)
    day = models.CharField('Day', max_length=1, choices=DAYS)
    turn = models.TimeField('Draw schedule')
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        unique_together = ('lottery', 'day', 'turn',)
        db_table = 'schedule'
    #
    def __str__(self):
        return '%s - %s - %s' % (self.lottery, self.DAYS[int(self.day)][1], self.turn)
#
class BettingAgency(models.Model):
    name = models.CharField('Name of betting agency', max_length=150)
    tax_id = models.CharField('Tax Identification Number', max_length=15)
    description = models.CharField('Betting agency description', max_length=512, null=True, blank=True)
    currency = models.CharField('Currency', max_length=2, choices=[(str(i), settings.CURRENCY[i]) for i in range(0, len(settings.CURRENCY))])
    minimum_bet = models.PositiveIntegerField('Minimum bet')
    system_commission = models.PositiveSmallIntegerField('System Commission Percentage', default=0)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'betting_agency'
        verbose_name = 'Betting Agency'
    #
    def get_lotteries(self):
        lotteries = self.pattern_set.values_list('lottery', flat=True).distinct()
        return Lottery.objects.filter(pk__in=lotteries)
    #
    def __str__(self): return self.name
#
class Icon(models.Model):
    name = models.CharField('Name of icon', max_length=150)
    identifier = models.PositiveIntegerField('Numeric Identifier')
    picture = models.ImageField('Logo', upload_to='icon', null=True, blank=True)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'icon'
    #
    def __str__(self): return '%d - %s' % (self.identifier, self.name)
#
class Pattern(models.Model):
    betting_agency = models.ForeignKey(BettingAgency, on_delete=models.CASCADE)
    lottery = models.ForeignKey(Lottery, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    bet_multiplier = models.PositiveIntegerField('Bet multiplier')
    minimum_bet = models.PositiveIntegerField('Minimum bet')
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        unique_together = ('betting_agency', 'lottery', 'icon',)
        db_table = 'pattern'
    #
    def __str__(self):
        return '%s - %s - %s' % (self.betting_agency, self.lottery, self.icon)