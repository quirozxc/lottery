from django.conf import settings

def get_tax_prefix(request):
    return { 'TAX_PREFIX': settings.TAX_PREFIX, }
#
def get_default_password(request):
    return { 'DEFAULT_PASSWORD': settings.DEFAULT_PASSWORD, }
#
def get_max_commission_percent(request):
    return { 'MAX_COMMISSION_PERCENT': settings.MAX_COMMISSION_PERCENT, }