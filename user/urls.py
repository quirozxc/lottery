from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('index/', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('password-change/', views.password_change, name='password_change'),
    path('seller/<int:seller>/password/reset/', views.reset_password, name='reset_password'),
    path('seller/create/', views.create_seller, name='create_seller'),
    path('seller/list/', views.list_seller, name='list_seller'),
    path('seller/list/<int:post_invoice>', views.list_seller, name='list_seller'),
    path('seller/<int:seller>/edit/', views.edit_seller, name='edit_seller'),
]