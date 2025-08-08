from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import PantryItem
from recipes.models import Recipe, Ingredient, RecipeIngredient
from .forms import PantryItemForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from mealplans.models import MealPlan, MealPlanItem, ShoppingItem

@require_POST
@login_required
def add_to_mealplan(request):
    recipe_id = request.POST.get('recipe_id')
    if not recipe_id:
        return redirect('pantry_suggest_recipes')
    # For demo: add to the user's most recent meal plan, or create one if none exists
    mealplan, created = MealPlan.objects.get_or_create(owner=request.user, defaults={'title': 'Quick Add', 'start_date': None, 'end_date': None})
    MealPlanItem.objects.create(mealplan=mealplan, recipe_id=recipe_id, day='Unassigned')
    return redirect('mealplans_dashboard')



@login_required
@require_POST
def add_missing_to_shopping_list(request, recipe_pk):
    """
    Add all missing ingredients for the given recipe to the user's shopping list.
    """
    # Find the recipe
    recipe = get_object_or_404(Recipe, pk=recipe_pk)
    # Get user's pantry ingredient PKs
    pantry_items = PantryItem.objects.filter(user=request.user)
    pantry_ingredient_pks = set(item.ingredient.pk for item in pantry_items)
    # Find missing ingredients for this recipe
    recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
    missing_pks = recipe_ingredient_pks - pantry_ingredient_pks
    missing_ingredients = Ingredient.objects.filter(pk__in=missing_pks)
    # Add each missing ingredient to the shopping list if not already present
    added_count = 0
    for ingredient in missing_ingredients:
        obj, created = ShoppingItem.objects.get_or_create(user=request.user, ingredient=ingredient)
        if created:
            added_count += 1
    from django.contrib import messages
    if added_count:
        messages.success(request, f"{added_count} missing ingredient(s) added to your shopping list.")
    else:
        messages.info(request, "All missing ingredients were already in your shopping list.")
    return redirect('shopping_list')


from django.contrib.auth.decorators import login_required

@login_required
def pantry_dashboard(request):
    from .models import PantryItem
    from recipes.models import Recipe, Ingredient
    from .forms import PantryItemForm
    # My Pantry
    items = PantryItem.objects.filter(user=request.user)
    # Check if editing
    edit_mode = False
    item = None
    edit_pk = request.GET.get('edit')
    if edit_pk:
        try:
            item = PantryItem.objects.get(pk=edit_pk, user=request.user)
            form = PantryItemForm(instance=item)
            edit_mode = True
        except PantryItem.DoesNotExist:
            form = PantryItemForm()
    else:
        form = PantryItemForm()
    # Recipe Suggestions
    pantry_items = items
    pantry_ingredient_pks = set(item.ingredient.pk for item in pantry_items)
    recipes_only_pantry = []
    recipes_with_missing = []
    for recipe in Recipe.objects.all():
        recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
        has_pantry = bool(recipe_ingredient_pks & pantry_ingredient_pks)
        if not has_pantry:
            continue
        missing = recipe_ingredient_pks - pantry_ingredient_pks
        matched = recipe_ingredient_pks & pantry_ingredient_pks
        total = len(recipe_ingredient_pks)
        match_percentage = int((len(matched) / total) * 100) if total > 0 else 0
    # My Pantry
    items = PantryItem.objects.filter(user=request.user)
    # Check if editing
    edit_mode = False
    item = None
    edit_pk = request.GET.get('edit')
    if edit_pk:
        try:
            item = PantryItem.objects.get(pk=edit_pk, user=request.user)
            form = PantryItemForm(instance=item)
            edit_mode = True
        except PantryItem.DoesNotExist:
            form = PantryItemForm()
    else:
        form = PantryItemForm()
    # Recipe Suggestions: My Recipes, Community Recipes, Saved Recipes, TheMealDB
    import requests
    pantry_items = items
    pantry_ingredient_pks = set(item.ingredient.pk for item in pantry_items)
    pantry_ingredient_names = set(item.ingredient.name.lower() for item in pantry_items)
    recipes_only_pantry = []
    recipes_with_missing = []
    # My recipes
    my_recipes = Recipe.objects.filter(owner=request.user)
    # Community recipes (public, not owned by user)
    community_recipes = Recipe.objects.filter(is_public=True).exclude(owner=request.user)
    # Saved recipes (recipes user has saved from others)
    try:
        from recipes.models import SavedRecipe
        saved_recipes = Recipe.objects.filter(saved_by__user=request.user)
    except ImportError:
        saved_recipes = Recipe.objects.none()
    # Combine all recipes, avoiding duplicates
    all_recipes = set(list(my_recipes) + list(community_recipes) + list(saved_recipes))
    # Add local recipes
    for recipe in all_recipes:
        recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
        has_pantry = bool(recipe_ingredient_pks & pantry_ingredient_pks)
        if not has_pantry:
            continue
        missing = recipe_ingredient_pks - pantry_ingredient_pks
        matched = recipe_ingredient_pks & pantry_ingredient_pks
        total = len(recipe_ingredient_pks)
        match_percentage = int((len(matched) / total) * 100) if total > 0 else 0
        if not missing:
            recipes_only_pantry.append({
                'recipe': recipe,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
                'source': 'local',
            })
        else:
            missing_ingredients = Ingredient.objects.filter(pk__in=missing)
            missing_ids = list(missing)
            recipes_with_missing.append({
                'recipe': recipe,
                'missing_ingredients': missing_ingredients,
                'missing_ingredient_ids': missing_ids,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
                'source': 'local',
            })

    # Add TheMealDB API recipes (default query: 'chicken')
    try:
        api_query = request.GET.get('api_query', 'chicken')
        url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={api_query}'
        response = requests.get(url, timeout=5)
        data = response.json()
        api_meals = data.get('meals') or []
        for meal in api_meals:
            meal_ingredients = set()
            missing_ingredients = []
            api_ingredients = []
            for i in range(1, 21):
                ing_name = meal.get(f'strIngredient{i}')
                if ing_name and ing_name.strip():
                    ing_name_clean = ing_name.strip().lower()
                    meal_ingredients.add(ing_name_clean)
                    api_ingredients.append(ing_name.strip())
                    if ing_name_clean not in pantry_ingredient_names:
                        missing_ingredients.append(ing_name_clean)
            matched = meal_ingredients & pantry_ingredient_names
            total = len(meal_ingredients)
            match_percentage = int((len(matched) / total) * 100) if total > 0 else 0
            if not missing_ingredients:
                recipes_only_pantry.append({
                    'recipe': meal,
                    'api_ingredients': api_ingredients,
                    'match_percentage': match_percentage,
                    'recipe_id': meal.get('idMeal'),
                    'source': 'api',
                })
            else:
                recipes_with_missing.append({
                    'recipe': meal,
                    'api_ingredients': api_ingredients,
                    'missing_ingredients': missing_ingredients,
                    'missing_ingredient_ids': [],
                    'match_percentage': match_percentage,
                    'recipe_id': meal.get('idMeal'),
                    'source': 'api',
                })
    except Exception:
        pass
    context = {
        'items': items,
        'form': form,
        'item': item,
        'edit_mode': edit_mode,
        'recipes_only_pantry': recipes_only_pantry,
        'recipes_with_missing': recipes_with_missing,
    }
    return render(request, 'pantry/pantry_tabs.html', context)


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
            if pantry_item.ingredient and pantry_item.amount:
                pantry_item.user = request.user
                pantry_item.save()
                from django.contrib import messages
                messages.success(request, "Pantry item added!")
                # Redirect to dashboard to reset form and show updated list
                return redirect('pantry_dashboard')
            else:
                from django.contrib import messages
                messages.error(request, "Please provide at least an ingredient and amount.")
        # If not valid, fall through to show form with errors
    else:
        form = PantryItemForm()
    # Always show a blank form after add, and show dashboard view
    items = PantryItem.objects.filter(user=request.user)
    # Recipe Suggestions logic (same as pantry_dashboard)
    pantry_ingredient_pks = set(item.ingredient.pk for item in items)
    recipes_only_pantry = []
    recipes_with_missing = []
    # My recipes
    my_recipes = Recipe.objects.filter(owner=request.user)
    # Community recipes (public, not owned by user)
    community_recipes = Recipe.objects.filter(is_public=True).exclude(owner=request.user)
    # Saved recipes (recipes user has saved from others)
    try:
        from recipes.models import SavedRecipe
        saved_recipes = Recipe.objects.filter(saved_by__user=request.user)
    except ImportError:
        saved_recipes = Recipe.objects.none()
    all_recipes = set(list(my_recipes) + list(community_recipes) + list(saved_recipes))
    for recipe in all_recipes:
        recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
        has_pantry = bool(recipe_ingredient_pks & pantry_ingredient_pks)
        if not has_pantry:
            continue
        missing = recipe_ingredient_pks - pantry_ingredient_pks
        matched = recipe_ingredient_pks & pantry_ingredient_pks
        total = len(recipe_ingredient_pks)
        match_percentage = int((len(matched) / total) * 100) if total > 0 else 0
        if not missing:
            recipes_only_pantry.append({
                'recipe': recipe,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
            })
        else:
            missing_ingredients = Ingredient.objects.filter(pk__in=missing)
            missing_ids = list(missing)
            recipes_with_missing.append({
                'recipe': recipe,
                'missing_ingredients': missing_ingredients,
                'missing_ingredient_ids': missing_ids,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
            })
    context = {
        'items': items,
        'form': PantryItemForm(),
        'recipes_only_pantry': recipes_only_pantry,
        'recipes_with_missing': recipes_with_missing,
    }
    return render(request, 'pantry/pantry_tabs.html', context)


@login_required
def pantry_edit(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    from django.contrib import messages
    if request.method == 'POST':
        form = PantryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pantry item updated successfully!')
            return redirect(f"/pantry/dashboard/?edit={item.pk}")
    else:
        form = PantryItemForm(instance=item)
    # Render the edit form using the dashboard, with the edit form open and pre-filled
    from django.template.response import TemplateResponse
    items = PantryItem.objects.filter(user=request.user)
    # Recipe Suggestions logic (same as dashboard)
    pantry_ingredient_pks = set(i.ingredient.pk for i in items)
    recipes_only_pantry = []
    recipes_with_missing = []
    from recipes.models import Recipe, Ingredient
    for recipe in Recipe.objects.all():
        recipe_ingredient_pks = set(recipe.ingredients.values_list('pk', flat=True))
        has_pantry = bool(recipe_ingredient_pks & pantry_ingredient_pks)
        if not has_pantry:
            continue
        missing = recipe_ingredient_pks - pantry_ingredient_pks
        matched = recipe_ingredient_pks & pantry_ingredient_pks
        total = len(recipe_ingredient_pks)
        match_percentage = int((len(matched) / total) * 100) if total > 0 else 0
        if not missing:
            recipes_only_pantry.append({
                'recipe': recipe,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
            })
        else:
            missing_ingredients = Ingredient.objects.filter(pk__in=missing)
            missing_ids = list(missing)
            recipes_with_missing.append({
                'recipe': recipe,
                'missing_ingredients': missing_ingredients,
                'missing_ingredient_ids': missing_ids,
                'match_percentage': match_percentage,
                'recipe_id': recipe.pk,
            })
    context = {
        'items': items,
        'form': form,
        'item': item,
        'edit_mode': True,
        'recipes_only_pantry': recipes_only_pantry,
        'recipes_with_missing': recipes_with_missing,
    }
    return TemplateResponse(request, 'pantry/pantry_tabs.html', context)


@login_required
def pantry_delete(request, pk):
    item = get_object_or_404(PantryItem, pk=pk, user=request.user)
    from django.contrib import messages
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Pantry item deleted successfully!')
        return redirect('pantry_dashboard')
    return render(request, 'pantry/pantry_confirm_delete.html', {'item': item})