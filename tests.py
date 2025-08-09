from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from pantry.models import PantryItem
from recipes.models import Recipe, Ingredient
from mealplans.models import MealPlan, MealPlanItem, ShoppingItem

User = get_user_model()

class PantryItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.ingredient = Ingredient.objects.create(name='Tomato', unit='pcs')

    def test_create_pantry_item(self):
        item = PantryItem.objects.create(user=self.user, ingredient=self.ingredient, amount=2)
        self.assertEqual(str(item.ingredient), 'Tomato')
        self.assertEqual(item.amount, 2)

    def test_edit_pantry_item(self):
        item = PantryItem.objects.create(user=self.user, ingredient=self.ingredient, amount=1)
        self.client.force_login(self.user)
        response = self.client.post(reverse('pantry_edit', args=[item.pk]), {
            'ingredient_name': 'Tomato',
            'amount': '5',
            'unit': 'pcs'
        }, follow=True)
        item.refresh_from_db()
        if item.amount != 5:
            print('DEBUG: Pantry edit response status:', response.status_code)
            print('DEBUG: Pantry edit response content:', response.content.decode(errors='replace'))
        self.assertEqual(item.amount, 5)

    def test_delete_pantry_item(self):
        item = PantryItem.objects.create(user=self.user, ingredient=self.ingredient, amount=1)
        self.client.force_login(self.user)
        response = self.client.post(reverse('pantry_delete', args=[item.pk]))
        self.assertFalse(PantryItem.objects.filter(pk=item.pk).exists())

class RecipeTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.force_login(self.user)

    def test_create_recipe(self):
        response = self.client.post(reverse('recipe_create'), {
            'title': 'Test Recipe',
            'description': 'Test description',
            'calories': '100',
            'is_public': True,
            'image': '',
            'recipeingredient_set-TOTAL_FORMS': '0',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000'
        }, follow=True)
        self.assertIn(response.status_code, [200, 302])
        if not Recipe.objects.filter(title='Test Recipe').exists():
            print('DEBUG: Recipe create response status:', response.status_code)
            print('DEBUG: Recipe create response content:', response.content.decode(errors='replace'))
            print('DEBUG: Recipe create form errors:', getattr(response, 'context', [{}])[0].get('form').errors if hasattr(response, 'context') and response.context else 'No context')
        self.assertTrue(Recipe.objects.filter(title='Test Recipe').exists())

    def test_edit_recipe(self):
        recipe = Recipe.objects.create(title='Old', owner=self.user)
        response = self.client.post(reverse('recipe_update', args=[recipe.pk]), {
            'title': 'New',
            'description': 'desc',
            'calories': '50',
            'is_public': True,
            'image': '',
            'recipeingredient_set-TOTAL_FORMS': '0',
            'recipeingredient_set-INITIAL_FORMS': '0',
            'recipeingredient_set-MIN_NUM_FORMS': '0',
            'recipeingredient_set-MAX_NUM_FORMS': '1000'
        }, follow=True)
        recipe.refresh_from_db()
        if recipe.title != 'New':
            print('DEBUG: Recipe edit response status:', response.status_code)
            print('DEBUG: Recipe edit response content:', response.content.decode(errors='replace'))
            print('DEBUG: Recipe edit form errors:', getattr(response, 'context', [{}])[0].get('form').errors if hasattr(response, 'context') and response.context else 'No context')
        self.assertEqual(recipe.title, 'New')

    def test_delete_recipe(self):
        recipe = Recipe.objects.create(title='DeleteMe', owner=self.user)
        response = self.client.post(reverse('recipe_delete', args=[recipe.pk]))
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

class MealPlanTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.force_login(self.user)

    def test_create_mealplan(self):
        import datetime
        response = self.client.post(reverse('mealplan_create'), {'week_start_date': datetime.date.today()})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MealPlan.objects.filter(owner=self.user, week_start_date=datetime.date.today()).exists())

class ShoppingListTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.client.force_login(self.user)
        self.ingredient = Ingredient.objects.create(name='Carrot', unit='pcs')
        import datetime
        self.mealplan = MealPlan.objects.create(owner=self.user, week_start_date=datetime.date.today())
        self.recipe = Recipe.objects.create(title='Carrot Soup', owner=self.user)
        from recipes.models import RecipeIngredient
        RecipeIngredient.objects.create(recipe=self.recipe, ingredient=self.ingredient, amount=1)
        self.mealplanitem = MealPlanItem.objects.create(mealplan=self.mealplan, recipe=self.recipe, day_of_week='Monday', meal_type='Lunch')
        # Add PantryItem so ShoppingItem can be created
        PantryItem.objects.create(user=self.user, ingredient=self.ingredient, amount=2)

    def test_generate_shopping_list(self):
        response = self.client.post(
            reverse('add_to_shopping_list'),
            {'api_id': self.recipe.title, 'mealplan_id': self.mealplan.pk}
        )
        self.assertEqual(response.status_code, 302)
        # ...existing code...
        if not ShoppingItem.objects.filter(mealplan=self.mealplan, ingredient=self.ingredient).exists():
            print('DEBUG: ShoppingList response status:', response.status_code)
            print('DEBUG: ShoppingList response content:', response.content.decode(errors='replace'))
            print('DEBUG: ShoppingItem not created. ShoppingItems:', list(ShoppingItem.objects.all()))
            print('DEBUG: MealPlan:', self.mealplan)
            print('DEBUG: MealPlan Items:', list(MealPlanItem.objects.filter(mealplan=self.mealplan)))
            print('DEBUG: Recipe:', self.recipe)
            print('DEBUG: Pantry Items:', list(PantryItem.objects.filter(user=self.user)))
        self.assertTrue(ShoppingItem.objects.filter(mealplan=self.mealplan, ingredient=self.ingredient).exists())

class PermissionsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user('user1', 'user1@example.com', 'pass')
        self.user2 = User.objects.create_user('user2', 'user2@example.com', 'pass')
        self.ingredient = Ingredient.objects.create(name='Egg', unit='pcs')
        self.item = PantryItem.objects.create(user=self.user2, ingredient=self.ingredient, amount=1)

    def test_edit_other_user_item_forbidden(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('pantry_edit', args=[self.item.pk]), {'ingredient': self.ingredient.pk, 'amount': 10})
        self.assertNotEqual(response.status_code, 302)

    def test_delete_other_user_item_forbidden(self):
        self.client.force_login(self.user1)
        response = self.client.post(reverse('pantry_delete', args=[self.item.pk]))
        self.assertNotEqual(response.status_code, 302)
