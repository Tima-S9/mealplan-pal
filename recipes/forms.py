from django import forms
from .models import RecipeIngredient, Ingredient

# Form for a single ingredient+amount for a recipe
class RecipeIngredientForm(forms.ModelForm):
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all(), label="Ingredient")
    amount = forms.FloatField(label="Amount")

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'amount']
from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'is_public']
