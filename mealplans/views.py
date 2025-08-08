from recipes.models import Recipe
from .models import MealPlanItem
from pantry.models import PantryItem

def mealplan_calendar(request):
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    meals = ['Breakfast', 'Lunch', 'Dinner']
    recipes = Recipe.objects.filter(owner=request.user)
    # For demo: get all mealplan items for the user (should be filtered by active plan)
    mealplan_items = MealPlanItem.objects.filter(mealplan__owner=request.user)
    slot_map = {}
    for item in mealplan_items:
        slot_map[(item.day, item.meal)] = item.recipe
    return render(request, 'mealplans/calendar.html', {
        'week_days': week_days,
        'meals': meals,
        'recipes': recipes,
        'slot_map': slot_map,
    })
from recipes.models import Ingredient

# Create shopping list from mealplan selected recipes
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def create_shopping_list_from_mealplan(request):
    if request.method == 'POST':
        missing_ids = request.POST.get('missing_ingredients', '').split(',')
        for ingredient_id in missing_ids:
            if ingredient_id:
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                ShoppingItem.objects.create(user=request.user, ingredient=ingredient)
        return redirect('shopping_list')
# Dashboard view for Mealplans
from django.contrib.auth.decorators import login_required

@login_required
def mealplans_dashboard(request):
    return render(request, 'mealplans/dashboard.html')
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
    missing_ingredient_ids = []

    if request.method == 'POST':
        selected_recipe_pks = []
        for day in week_days:
            pk = request.POST.get(f'recipe_{day}')
            if pk:
                selected_recipe_pks.append(pk)
        selected_recipes = Recipe.objects.filter(pk__in=selected_recipe_pks)

        # Aggregate ingredients and amounts
        ingredient_totals = {}
        all_ingredient_pks = set()
        for recipe in selected_recipes:
            for ri in RecipeIngredient.objects.filter(recipe=recipe):
                key = (ri.ingredient.pk, ri.ingredient.name, ri.ingredient.unit)
                if key not in ingredient_totals:
                    ingredient_totals[key] = ri.amount
                else:
                    ingredient_totals[key] += ri.amount
                all_ingredient_pks.add(ri.ingredient.pk)
        shopping_ingredients = [
            {'name': name, 'unit': unit, 'total_amount': round(amount, 2)}
            for (_, name, unit), amount in ingredient_totals.items()
        ]
        # Get user's pantry ingredient PKs
        pantry_items = PantryItem.objects.filter(user=request.user)
        pantry_ingredient_pks = set(item.ingredient.pk for item in pantry_items)
        missing_ingredient_ids = list(all_ingredient_pks - pantry_ingredient_pks)
        return render(request, 'mealplans/mealplan_create.html', {
            'week_days': week_days,
            'recipes': recipes,
            'shopping_ingredients': shopping_ingredients,
            'missing_ingredient_ids': missing_ingredient_ids,
        })

    return render(request, 'mealplans/mealplan_create.html', {
        'week_days': week_days,
        'recipes': recipes,
        'missing_ingredient_ids': [],
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