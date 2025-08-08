
from django import forms
from .models import MealPlan, MealPlanItem

# Simple MealPlan creation form
class SimpleMealPlanForm(forms.ModelForm):
    class Meta:
        model = MealPlan
        fields = ['week_start_date']

from django.contrib.auth.decorators import login_required

# View for creating a new meal plan
@login_required
def mealplan_create(request):
    if request.method == 'POST':
        form = SimpleMealPlanForm(request.POST)
        if form.is_valid():
            mealplan = form.save(commit=False)
            mealplan.owner = request.user
            mealplan.save()
            from django.urls import reverse
            return redirect(reverse('mealplan_list'))
    else:
        form = SimpleMealPlanForm()
    return render(request, 'mealplans/mealplan_create.html', {'form': form})
from recipes.models import Recipe
from .models import MealPlan, MealPlanItem
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

@login_required
def mealplan_list(request):
    # For the unified tab: show the create form and the list
    from recipes.models import Recipe, RecipeIngredient, Ingredient
    week_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    recipes = Recipe.objects.filter(owner=request.user)
    plans = MealPlan.objects.filter(owner=request.user)
    shopping_ingredients = None
    missing_ingredient_ids = []

    if request.method == 'POST':
        week_start_date = request.POST.get('week_start_date')
        selected_recipe_pks = []
        for day in week_days:
            pk = request.POST.get(f'recipe_{day}')
            if pk:
                selected_recipe_pks.append(pk)
        selected_recipes = Recipe.objects.filter(pk__in=selected_recipe_pks)

        # Create a new MealPlan for the selected week
        mealplan = MealPlan.objects.create(owner=request.user, week_start_date=week_start_date)

        # Add MealPlanItems for each selected recipe
        for day, pk in zip(week_days, selected_recipe_pks):
            if pk:
                MealPlanItem.objects.create(mealplan=mealplan, recipe_id=pk, day_of_week=day)

        # Aggregate ingredients and add to ShoppingItem
        ingredient_totals = {}
        for recipe in selected_recipes:
            for ri in RecipeIngredient.objects.filter(recipe=recipe):
                key = (ri.ingredient.pk, ri.ingredient)
                if key not in ingredient_totals:
                    ingredient_totals[key] = ri.amount
                else:
                    ingredient_totals[key] += ri.amount

        for (ingredient_pk, ingredient), amount in ingredient_totals.items():
            ShoppingItem.objects.update_or_create(
                mealplan=mealplan,
                ingredient=ingredient,
                defaults={'total_amount': amount}
            )

        # Redirect to the main shopping list tab
        from django.urls import reverse
        return redirect(reverse('shopping_list'))

    return render(request, 'mealplans/mealplan_unified.html', {
        'week_days': week_days,
        'recipes': recipes,
        'plans': plans,
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
    # Get all meal plans for the user, order by week
    plans = MealPlan.objects.filter(owner=request.user).order_by('-week_start_date')
    # Get selected mealplan_id from GET or POST
    mealplan_id = request.GET.get('mealplan_id') or request.POST.get('mealplan_id')
    selected_plan = None
    if mealplan_id:
        selected_plan = MealPlan.objects.filter(owner=request.user, id=mealplan_id).first()
    if not selected_plan and plans.exists():
        selected_plan = plans.first()
    # Only show items for the selected plan
    items = ShoppingItem.objects.filter(mealplan=selected_plan) if selected_plan else []
    if request.method == 'POST':
        for item in items:
            checked = request.POST.get(f'checked_{item.pk}') == 'on'
            if item.checked != checked:
                item.checked = checked
                item.save()
    return render(request, 'mealplans/shopping_list.html', {
        'shopping_items': items,
        'plans': plans,
        'selected_plan': selected_plan,
    })