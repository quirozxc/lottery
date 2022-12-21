from django.contrib import admin
from invoice.models import Commission, BettingAgencyInvoice, Invoice

# Register your models here.
admin.site.register(Commission)
admin.site.register(BettingAgencyInvoice)
admin.site.register(Invoice)