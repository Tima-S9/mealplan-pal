from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import MealPlan, MealPlanItem
from recipes.models import Recipe

@require_POST
def assign_recipe_to_slot(request):
    day = request.POST.get('day')
    meal = request.POST.get('meal')
    recipe_id = request.POST.get('recipe_id')
    user = request.user
    if not (day and meal and recipe_id):
        return JsonResponse({'success': False, 'error': 'Missing data'})
    # For demo: use or create a default meal plan for the user
    mealplan, _ = MealPlan.objects.get_or_create(owner=user, defaults={'title': 'Quick Add', 'start_date': None, 'end_date': None})
    # Remove any existing assignment for this slot
    MealPlanItem.objects.filter(mealplan=mealplan, day=day, meal=meal).delete()
    # Assign the new recipe
    MealPlanItem.objects.create(mealplan=mealplan, recipe_id=recipe_id, day=day, meal=meal)
    return JsonResponse({'success': True})
