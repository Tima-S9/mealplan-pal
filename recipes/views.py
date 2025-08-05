from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from .models import Recipe
from .forms import RecipeForm


class HomeView(TemplateView):
    template_name = "recipes/home.html"


def recipes_dashboard(request):
    return render(request, 'recipes/dashboard.html')


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
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.owner = request.user
            recipe.save()
            form.save_m2m()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()
    return render(request, 'recipes/recipe_form.html', {'form': form})


@login_required
def recipe_update(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm(instance=recipe)
    return render(request, 'recipes/recipe_form.html', {'form': form, 'recipe': recipe})


@login_required
def recipe_delete(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, owner=request.user)
    if request.method == 'POST':
        recipe.delete()
        return redirect('recipe_list')
    return render(request, 'recipes/recipe_confirm_delete.html', {'recipe': recipe})


def external_recipes(request):
    query = request.GET.get('q', 'chicken')  # Default search term
    url = f'https://www.themealdb.com/api/json/v1/1/search.php?s={query}'
    response = requests.get(url)
    data = response.json()
    meals = data.get('meals', [])
    return render(request, 'recipes/external_recipes.html', {'meals': meals, 'query': query})