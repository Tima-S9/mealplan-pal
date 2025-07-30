from django.contrib import admin
from .models import MealPlan, MealPlanItem, ShoppingItem

# Register your models here.
admin.site.register(MealPlan)
admin.site.register(MealPlanItem)
admin.site.register(ShoppingItem)



