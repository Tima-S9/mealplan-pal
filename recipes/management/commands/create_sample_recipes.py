from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recipes.models import Recipe, Ingredient


class Command(BaseCommand):
    help = 'Create sample recipes for testing'

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found. Please create a user first.'))
            return

        # Sample ingredients
        ingredients = [
            Ingredient.objects.get_or_create(name='Pasta', unit='g')[0],
            Ingredient.objects.get_or_create(name='Chicken Breast', unit='g')[0],
            Ingredient.objects.get_or_create(name='Rice', unit='g')[0],
            Ingredient.objects.get_or_create(name='Beef', unit='g')[0],
            Ingredient.objects.get_or_create(name='Tomato', unit='pcs')[0],
            Ingredient.objects.get_or_create(name='Lettuce', unit='pcs')[0],
            Ingredient.objects.get_or_create(name='Cheese', unit='g')[0],
            Ingredient.objects.get_or_create(name='Beans', unit='g')[0],
            Ingredient.objects.get_or_create(name='Broccoli', unit='g')[0],
            Ingredient.objects.get_or_create(name='Carrot', unit='g')[0],
        ]

        # Sample recipes
        recipes = [
            {
                'title': 'Classic Pasta',
                'description': 'A simple and delicious pasta dish.',
                'calories': 400,
                'is_public': True,
                'ingredients': [ingredients[0], ingredients[4], ingredients[6]],
            },
            {
                'title': 'Grilled Chicken',
                'description': 'Juicy grilled chicken breast with herbs.',
                'calories': 350,
                'is_public': True,
                'ingredients': [ingredients[1], ingredients[4], ingredients[5]],
            },
            {
                'title': 'Rice Salad',
                'description': 'Fresh rice salad with veggies.',
                'calories': 320,
                'is_public': True,
                'ingredients': [ingredients[2], ingredients[5], ingredients[9]],
            },
            {
                'title': 'Beef Stir Fry',
                'description': 'Tender beef with broccoli and carrots.',
                'calories': 500,
                'is_public': True,
                'ingredients': [ingredients[3], ingredients[8], ingredients[9]],
            },
            {
                'title': 'Vegetarian Chili',
                'description': 'Hearty chili with beans and veggies.',
                'calories': 280,
                'is_public': True,
                'ingredients': [ingredients[7], ingredients[8], ingredients[9]],
            },
        ]

        from recipes.models import RecipeIngredient
        for data in recipes:
            recipe, created = Recipe.objects.get_or_create(
                title=data['title'],
                defaults={
                    'description': data['description'],
                    'calories': data['calories'],
                    'owner': user,
                    'is_public': data['is_public'],
                }
            )
            if created:
                # Add each ingredient with a default amount
                for ingredient in data['ingredients']:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=100.0  # default amount
                    )
                recipe.save()
                self.stdout.write(self.style.SUCCESS(f"Created recipe: {recipe.title}"))
            else:
                self.stdout.write(f"Recipe already exists: {recipe.title}")

        self.stdout.write(self.style.SUCCESS('Sample recipes created.'))
