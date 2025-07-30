from django import forms
from .models import PantryItem


class PantryItemForm(forms.ModelForm):
    class Meta:
        model = PantryItem
        fields = ['ingredient', 'amount']
