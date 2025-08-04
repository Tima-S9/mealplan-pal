from django.urls import path
from . import views

urlpatterns = [
    path('', views.pantry_list, name='pantry_list'),
    path('add/', views.pantry_add, name='pantry_add'),
]
