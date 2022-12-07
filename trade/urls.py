from django.urls import path

from . import views

urlpatterns = [
    path('lottery/<int:lottery>/sell-ticket/', views.sell_ticket, name='sell_ticket'),
    path('ticket/<int:ticket>/status/', views.ticket_status, name='ticket_status'),
    path('ticket/<int:ticket>/status/<int:post_sale>/', views.ticket_status, name='ticket_status'),
    path('ticket/last/', views.last_ticket, name='last_ticket'),
    path('ticket/<int:ticket>/invalidate/', views.invalidate_ticket, name='invalidate_ticket'),
    path('ticket/<int:ticket>/print/', views.print_ticket, name='print_ticket'),
]