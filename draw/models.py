from django.db import models
from lottery.models import Schedule, Icon

from datetime import datetime

# Create your models here.
class Draw(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    def get_available_turns(self, lottery):
        return self.objects.filter(schedule__lottery__exact=lottery).filter(schedule__day__exact=datetime.today().weekday()) or None
    class Meta:
        db_table = 'draw'

class DrawResult(models.Model):
    draw = models.ForeignKey(Draw, on_delete=models.CASCADE)
    icon = models.ForeignKey(Icon, on_delete=models.CASCADE)
    #
    timestamp = models.DateTimeField(auto_now_add=True)
    #
    class Meta:
        db_table = 'draw_result'
        verbose_name = 'Draw Result'