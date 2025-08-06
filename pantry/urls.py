from django.urls import path
from . import views

urlpatterns = [
    path('add-to-mealplan/', views.add_to_mealplan, name='add_to_mealplan'),
    path('add-missing-to-shopping-list/', views.add_missing_to_shopping_list, name='add_missing_to_shopping_list'),
    path('dashboard/', views.pantry_dashboard, name='pantry_dashboard'),
    path('', views.pantry_list, name='pantry_list'),
    path('add/', views.pantry_add, name='pantry_add'),
    path('edit/<int:pk>/', views.pantry_edit, name='pantry_edit'),
    path('delete/<int:pk>/', views.pantry_delete, name='pantry_delete'),
    path('suggest/', views.pantry_suggest_recipes, name='pantry_suggest_recipes'),
]
