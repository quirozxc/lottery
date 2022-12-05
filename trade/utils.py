from django.conf import settings

def get_currency_badge(request):
    return { 'CURRENCY_BADGE': settings.CURRENCY_BADGE, }

def get_minimum_bet(request):
    return { 'MINIMUN_BET': settings.MINIMUM_BET, }