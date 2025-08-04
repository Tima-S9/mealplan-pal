from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import PantryItem
from .forms import PantryItemForm


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