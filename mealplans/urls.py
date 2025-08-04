from django.urls import path
from . import views

urlpatterns = [
    path('', views.mealplan_list, name='mealplan_list'),
    path('create/', views.mealplan_create, name='mealplan_create'),
    path('shopping/', views.shopping_list, name='shopping_list'),
    path('edit/<int:pk>/', views.mealplan_edit, name='mealplan_edit'),
    path('delete/<int:pk>/', views.mealplan_delete, name='mealplan_delete'),
]
