
from django.urls import path
from . import views
from . import views_ajax

urlpatterns = [
    path('assign-recipe/', views_ajax.assign_recipe_to_slot, name='assign_recipe_to_slot'),
    path('calendar/', views.mealplan_calendar, name='mealplan_calendar'),
    path('create-shopping-list/', views.create_shopping_list_from_mealplan, name='create_shopping_list_from_mealplan'),
    path('dashboard/', views.mealplans_dashboard, name='mealplans_dashboard'),
    path('', views.mealplan_list, name='mealplan_list'),
    path('create/', views.mealplan_create, name='mealplan_create'),
    path('shopping/', views.shopping_list, name='shopping_list'),
    path('edit/<int:pk>/', views.mealplan_edit, name='mealplan_edit'),
    path('delete/<int:pk>/', views.mealplan_delete, name='mealplan_delete'),
]
