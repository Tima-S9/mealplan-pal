from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import PantryItem
from recipes.models import Recipe, Ingredient, RecipeIngredient
from .forms import PantryItemForm

# Add missing ingredients to shopping list from pantry suggestions
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def add_missing_to_shopping_list(request):
    if request.method == 'POST':
        missing_ids = request.POST.get('missing_ingredients', '').split(',')
        for ingredient_id in missing_ids:
            if ingredient_id:
                ingredient = Ingredient.objects.get(pk=ingredient_id)
                ShoppingItem.objects.create(user=request.user, ingredient=ingredient)
        return redirect('shopping_list')


def pantry_dashboard(request):
    return render(request, 'pantry/dashboard.html')


@login_required
def pantry_suggest_recipes(request):
    # Get user's pantry ingredient PKs
    pantry_items = PantryItem.objects.filter(user=request.user)
    pantry_ingredient_pks = set(item.ingredient.pk for item in pantry_items)

    # Recipes that use only pantry ingredients
    recipes_only_pantry = []
    recipes_with_missing = []

    for recipe in Recipe.objects.all():
        recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
        has_pantry = bool(recipe_ingredient_pks & pantry_ingredient_pks)
        if not has_pantry:
            continue  # Skip recipes with no pantry items
        missing = recipe_ingredient_pks - pantry_ingredient_pks
        if not missing:
            recipes_only_pantry.append(recipe)
        else:
            missing_ingredients = Ingredient.objects.filter(pk__in=missing)
            missing_ids = list(missing)
            recipes_with_missing.append({
                'recipe': recipe,
                'missing_ingredients': missing_ingredients,
                'missing_ingredient_ids': missing_ids,
            })

    return render(request, 'pantry/pantry_suggest_recipes.html', {
        'recipes_only_pantry': recipes_only_pantry,
        'recipes_with_missing': recipes_with_missing,
    })



# Create your views here.
def index(request):
    return HttpResponse("Welcome to the Pantry!") 


@login_required
def pantry_list(request):
    items = PantryItem.objects.filter(user=request.user)
    return render(request, 'pantry/pantry_list.html', {'items': items})


@login_required
def pantry_add(request):
    if request.method == 'POST':
        form = PantryItemForm(request.POST)
        if form.is_valid():
            pantry_item = form.save(commit=False)
            pantry_item.user = request.user
            pantry_item.save()
            return redirect('pantry_list')
    else:
        form = PantryItemForm()
    return render(request, 'pantry/pantry_form.html', {'form': form})


@login_required
def pantry_edit(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PantryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('pantry_list')
    else:
        form = PantryItemForm(instance=item)
    return render(request, 'pantry/pantry_form.html', {'form': form, 'item': item})


@login_required
def pantry_delete(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('pantry_list')
    return render(request, 'pantry/pantry_confirm_delete.html', {'item': item})