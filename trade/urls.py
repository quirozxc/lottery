from django.urls import path

from . import views

urlpatterns = [
    path('lottery/<int:lottery>/sell-ticket/', views.sell_ticket, name='sell_ticket'),
    path('ticket/<int:ticket>/details/', views.ticket, name='ticket'),
    path('ticket/<int:ticket>/post-sale/<int:post_sale>/', views.ticket, name='ticket'),
    path('ticket/last/', views.last_ticket, name='last_ticket'),
    path('ticket/<int:ticket>/invalidate/', views.invalidate_ticket, name='invalidate_ticket'),
    path('ticket/<int:ticket>/print/', views.print_ticket, name='print_ticket'),
    path('search/', views.search_ticket, name='search_ticket'),
    path('ticket/<int:ticket>/winner/', views.winning_ticket, name='winning_ticket'),
    path('ticket/<int:winner_ticket>/pay/', views.pay_ticket, name='pay_ticket'),
    path('export/', views.export_trade, name='export_trade'),
]