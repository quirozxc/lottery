from django.contrib import admin
from invoice.models import Commission, Invoice, RowInvoice

# Register your models here.
admin.site.register(Commission)
admin.site.register(Invoice)
admin.site.register(RowInvoice)