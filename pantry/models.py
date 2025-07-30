from django.db import models
from django.contrib.auth.models import User
from recipes.models import Ingredient


# Create your models here.
class PantryItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.FloatField()

    def __str__(self):
        return f"{self.amount} {self.ingredient.unit} {self.ingredient.name} for {self.user.username}"

