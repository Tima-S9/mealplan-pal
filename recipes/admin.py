from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient

# Register your models here.
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(RecipeIngredient)



