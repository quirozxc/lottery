from django.contrib import admin
from .models import Ticket, RowTicket

# Register your models here.
class RowTicketInline(admin.TabularInline):
    model = RowTicket
    extra = 1
class TicketAdmin(admin.ModelAdmin):
    inlines = (RowTicketInline,)
admin.site.register(Ticket, TicketAdmin)

admin.site.register(RowTicket)