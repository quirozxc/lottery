from django.urls import path

from . import views

urlpatterns = [
    path('lottery/<int:lottery>/register/', views.draw_register, name='draw_register'),
    path('result/<int:draw_result>/confirm/', views.confirm_draw, name='confirm_draw'),
    path('result/<int:draw_result>/delete/', views.delete_draw, name='delete_draw'),
]