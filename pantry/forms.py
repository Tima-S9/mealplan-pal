from django import forms
from .models import PantryItem


class PantryItemForm(forms.ModelForm):

    ingredient_name = forms.CharField(label='Ingredient', max_length=100)
    amount = forms.FloatField(label='Amount', required=True)
    unit = forms.CharField(label='Unit', max_length=50, required=True)
    weight_in_grams = forms.FloatField(label='Weight (g)', required=False)

    class Meta:
        model = PantryItem
        fields = ['ingredient_name', 'amount', 'unit', 'weight_in_grams']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['ingredient_name'].initial = self.instance.ingredient.name
            self.fields['unit'].initial = self.instance.ingredient.unit

    def clean_ingredient_name(self):
        name = self.cleaned_data['ingredient_name'].strip()
        if not name:
            raise forms.ValidationError('Ingredient name cannot be empty.')
        return name

    def clean_unit(self):
        unit = self.cleaned_data['unit'].strip()
        if not unit:
            raise forms.ValidationError('Unit cannot be empty.')
        return unit

    def save(self, commit=True):
        from recipes.models import Ingredient
        name = self.cleaned_data['ingredient_name'].strip()
        unit = self.cleaned_data['unit'].strip()
        ingredient, _ = Ingredient.objects.get_or_create(name=name, defaults={'unit': unit})
        # If ingredient exists but unit is different, update it
        if ingredient.unit != unit:
            ingredient.unit = unit
            ingredient.save()
        self.instance.ingredient = ingredient
        return super().save(commit=commit)
