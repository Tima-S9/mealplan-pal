from django import forms
from .models import Recipe


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'image', 'is_public', 'ingredients']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple(),
        }
