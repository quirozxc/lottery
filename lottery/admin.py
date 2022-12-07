from django.contrib import admin
from .models import Lottery, Schedule, BettingAgency, Icon, Pattern

# Register your models here.

class ScheduleInline(admin.TabularInline):
    model = Schedule
    extra = 1
class LotteryAdmin(admin.ModelAdmin):
    list_display = ('name', 'picture', 'timestamp',)
    inlines = (ScheduleInline,)
admin.site.register(Lottery, LotteryAdmin)
#
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('lottery', 'day', 'turn', 'timestamp',)
admin.site.register(Schedule, ScheduleAdmin)
#
class PatternInline(admin.TabularInline):
    model = Pattern
    extra = 1
class BettingAgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'description',)
    inlines = (PatternInline,)
admin.site.register(BettingAgency, BettingAgencyAdmin)
#
class IconAdmin(admin.ModelAdmin):
    list_display = ('name', 'identifier', 'picture', 'timestamp',)
admin.site.register(Icon, IconAdmin)
#
class PatternAdmin(admin.ModelAdmin):
    list_display = ('betting_agency', 'lottery', 'icon', 'bet_multiplier', 'minimum_bet',)
admin.site.register(Pattern, PatternAdmin)