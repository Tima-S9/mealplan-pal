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
    if request.method == 'POST':
        form = MealPlanForm(request.POST)
        if form.is_valid():
            mealplan = form.save(commit=False)
            mealplan.owner = request.user
            mealplan.save()
            return redirect('mealplan_list')
    else:
        form = MealPlanForm()
    return render(request, 'mealplans/mealplan_form.html', {'form': form})

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
