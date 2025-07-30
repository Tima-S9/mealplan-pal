from django.db import models
from django.contrib.auth.models import User
from recipes.models import Recipe, Ingredient


# Create your models here.
class MealPlan(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    week_start_date = models.DateField()

    def __str__(self):
        return f"Meal Plan for {self.owner.username} starting {self.week_start_date}"


class MealPlanItem(models.Model):
    mealplan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, null=True)
    day_of_week = models.CharField(max_length=10)
    meal_type = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.meal_type} on {self.day_of_week}: {self.recipe}"


class ShoppingItem(models.Model):
    mealplan = models.ForeignKey(MealPlan, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    total_amount = models.FloatField()
    checked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.total_amount} {self.ingredient.unit} {self.ingredient.name} (Checked: {self.checked})"



