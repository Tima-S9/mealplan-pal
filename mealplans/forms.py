from django import forms
from .models import MealPlan, MealPlanItem, ShoppingItem


class MealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['week_start_date']


class MealPlanItemForm(forms.ModelForm):
    class Meta:
        model = MealPlanItem
        fields = ['recipe', 'day_of_week', 'meal_type']


class ShoppingItemForm(forms.ModelForm):
    class Meta:
        model = ShoppingItem
        fields = ['ingredient', 'total_amount', 'checked']
