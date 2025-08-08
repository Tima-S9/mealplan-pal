from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path("accounts/", include("allauth.urls")),
    path('dashboard/', views.recipes_dashboard, name='recipes_dashboard'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipe/new/', views.recipe_create, name='recipe_create'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:pk>/edit/', views.recipe_update, name='recipe_update'),
    path('recipes/<int:pk>/delete/', views.recipe_delete, name='recipe_delete'),
    path('recipes/external/', views.external_recipes, name='external_recipes'),
    path('recipes/save_api/', views.save_api_recipe, name='save_api_recipe'),
]
