from django.conf import settings

def get_tax_prefix(request):
    return { 'TAX_PREFIX': settings.TAX_PREFIX, }