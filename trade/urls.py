from django.urls import path

from . import views

urlpatterns = [
    path('lottery/<int:lottery>/sell-ticket/', views.sell_ticket, name='sell_ticket'),
    path('ticket/<int:ticket>/status/', views.ticket_status, name='ticket_status'),
]