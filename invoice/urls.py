from django.urls import path

from . import views

urlpatterns = [
    path('create/', views.create_invoice, name='create_invoice'),
    path('last/download/', views.export_invoice, name='export_invoice'),
    path('<int:betting_agency_invoice>/download/', views.export_invoice, name='export_invoice'),
]