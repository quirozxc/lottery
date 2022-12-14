from django_cron import CronJobBase, Schedule

from django.conf import settings
from datetime import datetime
from .models import Lottery
from draw.models import Draw

def is_holiday(holidays=settings.HOLIDAYS):
    for hdaystr in holidays:
        if datetime.today().strftime('%d/%m') == hdaystr: return True
    return False
#
def draw_job():
    if not is_holiday():
        for lottery in Lottery.objects.all():
            for turn in lottery.schedule_set.filter(day__exact=datetime.today().weekday()):
                Draw(schedule=turn).save()
#
class DrawJob(CronJobBase):
    RUN_AT_TIMES = ['00:00']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'lottery.draw_job'

    def do(self):
        draw_job()