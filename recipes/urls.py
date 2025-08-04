from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
]
