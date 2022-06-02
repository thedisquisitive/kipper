from dataclasses import asdict, dataclass, field
from typing import List, Dict, Any
from enum import IntEnum

import pymongo

kipper_client = pymongo.MongoClient('mongodb://localhost:27017/')
kipper_db = kipper_client["KipperDatabase"]

kipper_table_Recipe             = kipper_db["Recipe"]
kipper_table_Ingredient         = kipper_db["Ingredient"]
#kipper_table_RecipeIngredient   = kipper_db["RecipeIngredient"]

# Documents (rows) format
"""
    Collection : Recipe
        -recipeID
        -recipeName
        -course
    Collection : Ingredient
        -ingredientID
        -ingredientName
        -usedInTheseRecipes
    Collection : RecipeIngredient
        -recipeID
        -ingredientID
"""

class CourseEnum(IntEnum):
    BREAKFAST = 1
    LUNCH = 2
    DINNER = 3

@dataclass(repr=False)
class RecipeClass:
    recipeID: int
    recipeName: str
    course: CourseEnum
    ingredientIDs: list

@dataclass(repr=False)
class IngredientClass:
    ingredientID: int
    ingredientName: str
    usedInTheseRecipes: list = field(default_factory=list)

@dataclass(repr=False)
class RecipeIngredient:
    recipeID: int
    ingreidentID: int
    
def insert_recipe(recipe_name: str, course: CourseEnum, ingredient_IDs: List[int], *, table: pymongo.collection.Collection = kipper_table_Recipe,
                ingredient_table: pymongo.collection.Collection = kipper_table_Ingredient) -> None:
    recipe_ID = 0 if (last_entry := table.find_one(sort=[("recipeID", -1)])) is None else last_entry["recipeID"]+1

    recipe = RecipeClass(recipe_ID, recipe_name, course, ingredient_IDs)
    document = asdict(recipe)

    table.insert_one(document)
    
    for ingredient_ID in ingredient_IDs:
        ingredient = ingredient_table.find_one({"ingredientID": ingredient_ID})
        ingredient['usedInTheseRecipes'].append(recipe_ID)
        ingredient_table.update_one({"ingredientID": ingredient_ID}, {"$set": ingredient}, upsert=False)
        ingredient = ingredient_table.find_one({"ingredientID": ingredient_ID})

def insert_ingredient(ingredient_name: str, *, table: pymongo.collection.Collection = kipper_table_Ingredient) -> None:
    ingredient_ID = 0 if (last_entry := table.find_one(sort=[("ingredientID", -1)])) is None else last_entry["ingredientID"]+1

    ingredient = IngredientClass(ingredient_ID, ingredient_name)
    document = asdict(ingredient)

    table.insert_one(document)

def get_ingredient_id(ingredient_name: str, *, table: pymongo.collection.Collection = kipper_table_Ingredient) -> int:
    ingredient = table.find_one({"ingredientName": ingredient_name})
    return ingredient["ingredientID"]

def get_ingredient_name_from_id(ingredient_ID: int, *, table: pymongo.collection.Collection = kipper_table_Ingredient) -> str:
    ingredient = table.find_one({"ingredientID": ingredient_ID})
    if ingredient is None:
        return "NULL INGREDIENT!!"
    return ingredient["ingredientName"]

def delete_recipe_by_id(recipe_id: int, *, table: pymongo.collection.Collection = kipper_table_Recipe) -> None:
    document = {"recipeID": recipe_id}
    table.delete_one(document)

def ingredient_used_in(ingredient_id: int, *, table: pymongo.collection.Collection = kipper_table_Ingredient) -> None:
    ingredient = table.find_one({"ingredientID": ingredient_id})
    for recipe_id in ingredient['usedInTheseRecipes']:
        print(f"RecipeID: {recipe_id}")

def get_all_ingredients(*, table: pymongo.collection.Collection = kipper_table_Ingredient) -> List[Dict[int, str]]:
    ingredients = []
    for ingredient in table.find({}):
        ingredients.append({ingredient['ingredientID']: ingredient['ingredientName']})

    return ingredients

def get_all_recipes(*, table: pymongo.collection.Collection = kipper_table_Recipe) -> List[Dict[str, Any]]:
    recipes = []
    for recipe in table.find({}):
        recipes.append({'id': recipe["recipeID"], 'name': recipe["recipeName"], 'ingredientIDs': recipe['ingredientIDs'], 'course': CourseEnum(recipe['course']).name})

    return recipes

def get_current_recipe_id(*, table: pymongo.collection.Collection = kipper_table_Recipe) -> int:
    recipe_ID = 0 if (last_entry := table.find_one(sort=[("recipeID", -1)])) is None else last_entry["recipeID"]+1
    return recipe_ID

def get_smallest_recipe_id(*, table: pymongo.collection.Collection = kipper_table_Recipe) -> int:
    recipe_ID = 0 if (first_entry := table.find_one(sort=[("recipeID", 1)])) is None else first_entry["recipeID"]
    return recipe_ID

def drop_database(*, db_name: str = "KipperDatabase")-> None:
    kipper_client.drop_database(db_name)

#recipeIngredient_document   = {"recipeID": None, "ingredientID": None, "usedInTheseRecipes": []}
#kipper_table_RecipeIngredient.insert_one(recipeIngredient_document)

# TESTS
"""
insert_ingredient("Flour")
insert_ingredient("Sugar")
insert_ingredient("Eggs")
insert_ingredient("Baking Powder")
insert_ingredient("Banana")
insert_ingredient("Milk")
insert_recipe("Banana Bread", CourseEnum.DINNER, [0,1,2,3,4,5])
insert_recipe("Bread", CourseEnum.DINNER, [0,1,2,3,5])
"""
