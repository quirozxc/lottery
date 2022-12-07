from django.conf import settings

def get_currency_badge(request):
    return { 'CURRENCY_BADGE': settings.CURRENCY_BADGE, }

def get_minimum_bet(request):
    return { 'MINIMUN_BET': settings.MINIMUM_BET, }

def get_tax_prefix(request):
    return { 'TAX_PREFIX': settings.TAX_PREFIX, }