from django.urls import path

from . import views

urlpatterns = [
    path('betting-agency/list/', views.betting_agency_list, name='betting_agency_list'),
    path('betting-agency/<int:betting_agency>/edit/', views.edit_betting_agency, name='edit_betting_agency'),
]