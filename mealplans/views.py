# Shopping List View
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import MealPlan, MealPlanItem, ShoppingItem
from .forms import MealPlanForm, MealPlanItemForm, ShoppingItemForm


# Create your views here.
def index(request):
    return HttpResponse("Mealplans Home Page!")


@login_required
def mealplan_list(request):
    plans = MealPlan.objects.filter(owner=request.user)
    return render(request, 'mealplans/mealplan_list.html', {'plans': plans})


@login_required
def mealplan_create(request):
    from recipes.models import Recipe, RecipeIngredient, Ingredient
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    recipes = Recipe.objects.filter(owner=request.user)
    shopping_ingredients = None

    if request.method == 'POST':
        selected_recipe_pks = []
        for day in week_days:
            pk = request.POST.get(f'recipe_{day}')
            if pk:
                selected_recipe_pks.append(pk)
        selected_recipes = Recipe.objects.filter(pk__in=selected_recipe_pks)

        # Aggregate ingredients and amounts
        ingredient_totals = {}
        for recipe in selected_recipes:
            for ri in RecipeIngredient.objects.filter(recipe=recipe):
                key = (ri.ingredient.pk, ri.ingredient.name, ri.ingredient.unit)
                if key not in ingredient_totals:
                    ingredient_totals[key] = ri.amount
                else:
                    ingredient_totals[key] += ri.amount
        shopping_ingredients = [
            {'name': name, 'unit': unit, 'total_amount': round(amount, 2)}
            for (_, name, unit), amount in ingredient_totals.items()
        ]

        # Optionally, save MealPlan and MealPlanItems here
        # ...

        return render(request, 'mealplans/mealplan_create.html', {
            'week_days': week_days,
            'recipes': recipes,
            'shopping_ingredients': shopping_ingredients,
        })

    return render(request, 'mealplans/mealplan_create.html', {
        'week_days': week_days,
        'recipes': recipes,
    })


@login_required
def mealplan_edit(request, pk):
    plan = get_object_or_404(MealPlan, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = MealPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            return redirect('mealplan_list')
    else:
        form = MealPlanForm(instance=plan)
    return render(request, 'mealplans/mealplan_form.html', {'form': form, 'plan': plan})


@login_required
def mealplan_delete(request, pk):
    plan = get_object_or_404(MealPlan, pk=pk, owner=request.user)
    if request.method == 'POST':
        plan.delete()
        return redirect('mealplan_list')
    return render(request, 'mealplans/mealplan_confirm_delete.html', {'plan': plan})


@login_required
def shopping_list(request):
    items = ShoppingItem.objects.filter(mealplan__owner=request.user)
    if request.method == 'POST':
        for item in items:
            checked = request.POST.get(f'checked_{item.pk}') == 'on'
            if item.checked != checked:
                item.checked = checked
                item.save()
    return render(request, 'mealplans/shopping_list.html', {'shopping_items': items})