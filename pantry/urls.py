from django.urls import path
from . import views

urlpatterns = [
    path('', views.pantry_list, name='pantry_list'),
    path('add/', views.pantry_add, name='pantry_add'),
    path('edit/<int:pk>/', views.pantry_edit, name='pantry_edit'),
    path('delete/<int:pk>/', views.pantry_delete, name='pantry_delete'),
    path('suggest/', views.pantry_suggest_recipes, name='pantry_suggest_recipes'),
]
