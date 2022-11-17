from django.urls import path
from . import views

urlpatterns = [
    path('new_mail/', views.compose_mail, name='compose_mail'),
    path('read_mail/<int:pk>/', views.read_mail, name='read_mail'),
    path('correct_list/', views.theCorrectList, name='correct_list'),
    path('<str:type>/', views.home, name='mail-home'),
]