from .models import Recipe, SavedRecipe, RecipeIngredient, Ingredient
from .forms import RecipeForm, RecipeIngredientForm
from django.forms import inlineformset_factory, modelformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required
@login_required
def save_api_recipe(request):
    if request.method == 'POST':
        api_id = request.POST.get('api_id')
        title = request.POST.get('title')
        image_url = request.POST.get('image_url')
        category = request.POST.get('category')
        area = request.POST.get('area')
        source = request.POST.get('source')
        # Check if already saved
        if Recipe.objects.filter(title=title, owner=request.user).exists():
            messages.info(request, 'You have already saved this recipe.')
            return redirect(request.META.get('HTTP_REFERER', 'recipes_dashboard'))
        # Create a new Recipe instance for the user
        recipe = Recipe.objects.create(
            title=title,
            description=f"Imported from API ({category}, {area})",
            owner=request.user,
            is_public=False
        )
        # Optionally, download and save the image, or just store the URL if your model supports it
        # Save ingredients from TheMealDB API
        import requests
        api_url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={api_id}'
        api_response = requests.get(api_url)
        api_data = api_response.json()
        meal = None
        if api_data.get('meals'):
            meal = api_data['meals'][0]
        if meal:
            for i in range(1, 21):
                ing_name = meal.get(f'strIngredient{i}')
                ing_measure = meal.get(f'strMeasure{i}')
                if ing_name and ing_name.strip():
                    ing_obj, _ = Ingredient.objects.get_or_create(name=ing_name.strip(), defaults={'unit': ''})
                    # Try to extract a float from the measure, fallback to 1.0
                    try:
                        amount = float(ing_measure.split()[0]) if ing_measure and ing_measure.split()[0].replace('.', '', 1).isdigit() else 1.0
                    except Exception:
                        amount = 1.0
                    RecipeIngredient.objects.create(recipe=recipe, ingredient=ing_obj, amount=amount)
        # Save as a SavedRecipe
        SavedRecipe.objects.create(user=request.user, recipe=recipe)
        messages.success(request, 'Recipe saved to your collection!')
        return redirect(request.META.get('HTTP_REFERER', 'recipes_dashboard'))
from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import Recipe
from .forms import RecipeForm


class HomeView(TemplateView):
    template_name = "recipes/home.html"


from django.contrib.auth.decorators import login_required

@login_required
def recipes_dashboard(request):
    from .models import Recipe
    search_tab = request.GET.get('search_tab', 'my')
    query = request.GET.get('q', '')
    my_search_results = Recipe.objects.filter(owner=request.user)
    community_search_results = Recipe.objects.filter(is_public=True).exclude(owner=request.user)
    api_meals = []
    api_query = ''
    if search_tab == 'my' and query:
        my_search_results = my_search_results.filter(title__icontains=query)
    if search_tab == 'community' and query:
        community_search_results = community_search_results.filter(title__icontains=query)
    if search_tab == 'api':
        api_query = query or 'chicken'
        import requests
        url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={api_query}'
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            api_meals = data.get('meals') or []
        except Exception:
            api_meals = []
    context = {
        'search_tab': search_tab,
        'query': query,
        'my_search_results': my_search_results,
        'community_search_results': community_search_results,
        'meals': api_meals,
    }
    return render(request, 'recipes/dashboard.html', context)


def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['recipes'] = Recipe.objects.all()[:3]  # Show 3 recipes
    return context


def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})


def recipe_detail(request, pk):
    from .models import Recipe
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})


@login_required
def recipe_create(request):
    RecipeIngredientFormSet = inlineformset_factory(
        Recipe,
        RecipeIngredient,
        form=RecipeIngredientForm,
        extra=1,  # Always show one extra blank row
        can_delete=True,
        min_num=0,
        validate_min=False
    )
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        recipe = Recipe()  # Unsaved instance for inline formset
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        new_ingredient_name = request.POST.get('new_ingredient', '').strip()
        new_ingredient_unit = request.POST.get('new_ingredient_unit', '').strip()
        try:
            new_ingredient_amount = float(request.POST.get('new_ingredient_amount', '').strip())
        except Exception:
            new_ingredient_amount = None
        if form.is_valid() and formset.is_valid():
            recipe = form.save(commit=False)
            recipe.owner = request.user
            recipe.save()
            form.save_m2m()
            formset.instance = recipe
            formset.save()
            # Add new ingredient if provided
            if new_ingredient_name and new_ingredient_amount is not None:
                ingredient, _ = Ingredient.objects.get_or_create(name=new_ingredient_name, defaults={'unit': new_ingredient_unit})
                RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=new_ingredient_amount)
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
        recipe = Recipe()  # Unsaved instance for inline formset
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form, 'formset': formset})


@login_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    RecipeIngredientFormSet = inlineformset_factory(
        Recipe,
        RecipeIngredient,
        form=RecipeIngredientForm,
        extra=1,  # Always show one extra blank row
        can_delete=True,
        min_num=0,
        validate_min=False
    )
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)
        new_ingredient_name = request.POST.get('new_ingredient', '').strip()
        new_ingredient_unit = request.POST.get('new_ingredient_unit', '').strip()
        try:
            new_ingredient_amount = float(request.POST.get('new_ingredient_amount', '').strip())
        except Exception:
            new_ingredient_amount = None
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            # Add new ingredient if provided
            if new_ingredient_name and new_ingredient_amount is not None:
                ingredient, _ = Ingredient.objects.get_or_create(name=new_ingredient_name, defaults={'unit': new_ingredient_unit})
                RecipeIngredient.objects.create(recipe=recipe, ingredient=ingredient, amount=new_ingredient_amount)
            messages.success(request, 'Recipe updated successfully!')
            # Redirect to 'My Recipes' tab on dashboard
            return redirect('/recipes/dashboard/?search_tab=my')
    else:
        form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form, 'formset': formset, 'recipe': recipe})


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    if request.method == 'POST':
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!')
        return redirect('recipe_list')
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})


def external_recipes(request):
    query = request.GET.get('q', 'chicken')  # Default search term
    url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={query}'
    response = requests.get(url)
    data = response.json()
    meals = data.get('meals')
    if meals is None:
        meals = []
    return render(request, 'recipes/external_recipes.html', {'meals': meals, 'query': query})