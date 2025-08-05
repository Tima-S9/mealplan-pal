# mealplan-pal
# MealPlan Pal
## Overview
MealPlan Pal is a Django web application for meal planning, pantry management, and shopping list generation. It features grouped dashboards, external recipe search, and a modern Bootstrap UI.

## Table of Contents
1. Features
2. App Structure
3. Database Models
4. Wireframes
5. Color Palette
6. Diagrams
7. Setup

Features
### 🔧 Feature Overview

| Area      | Features                                                                 |
|-----------|--------------------------------------------------------------------------|
| Recipes   | CRUD, dashboard, external API search, recipe suggestions                 |
| Pantry    | CRUD, dashboard, recipe suggestions based on pantry, add missing items   |
| Mealplans | CRUD, dashboard, create shopping list from mealplan                      |
| Shopping  | Shopping list generated from pantry/mealplans                            |
| UI/UX     | Bootstrap 5, grouped navigation, active tab highlighting                 |


App Structure

### 🗂️ App Structure Overview

| App       | Key Files/Views                | Templates                        |
|-----------|-------------------------------|----------------------------------|
| recipes   | views.py, urls.py, dashboard  | dashboard.html, home.html        |
| pantry    | views.py, urls.py, dashboard  | dashboard.html, suggest.html     |
| mealplans | views.py, urls.py, dashboard  | dashboard.html, create.html      |

## Database Models

### 🧩 Data Model Overview

| Model           | Fields                                             |
|----------------|----------------------------------------------------|
| Recipe          | title, description, image, calories, owner        |
| Ingredient      | name, unit                                        |
| RecipeIngredient| recipe, ingredient, amount                        |
| PantryItem      | user, ingredient, amount                          |
| MealPlan        | owner, title, start_date, end_date                |
| MealPlanItem    | mealplan, recipe, day                             |
| ShoppingItem    | user, ingredient, amount                          |

## Wireframes

[Home Page]
+-------------------------------+
| MealPlan Pal                  |
|-------------------------------|
| [Recipes] [My Pantry] [Mealplans] |
+-------------------------------+

[Dashboard Example]
+-------------------------------+
| Recipes Dashboard             |
|-------------------------------|
| [My Recipes] [Create Recipe]  |
| [Search Recipes] [Shopping List] |
+-------------------------------+

## Color Palette

### 🎨 Color Palette

| Color Name    | Hex      | Usage                     |
|---------------|----------|---------------------------|
| Primary Blue  | #0d6efd | Navbar, buttons           |
| Success       | #198754 | Add/Create buttons        |
| Warning       | #ffc107 | Suggest/Shopping          |
| Dark          | #212529 | Footer, active tab        |
| Light         | #f8f9fa | Backgrounds               | 

## Diagrams
App Relationships

Recipe <-- RecipeIngredient --> Ingredient
MealPlan <-- MealPlanItem --> Recipe
User <-- PantryItem --> Ingredient
User <-- ShoppingItem --> Ingredient

## Setup
Clone the repo
Install requirements: pip install -r requirements.txt
Run migrations: python [manage.py](http://_vscodecontentref_/2) migrate
Start server: python [manage.py](http://_vscodecontentref_/3) runserver