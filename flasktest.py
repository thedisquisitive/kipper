from flask import Flask, request, url_for, render_template, redirect
import mongotest

app = Flask(__name__)

def get_recipes_and_ingredients():
    recipes = mongotest.get_all_recipes()
    ingredients = mongotest.get_all_ingredients()

    # Convert Ingredient ID list to Ingredient Names
    for recipe in recipes:
        name_list = []
        id_list = recipe['ingredientIDs']
        for id in id_list:
            name_list.append(mongotest.get_ingredient_name_from_id(id))
        recipe['ingredientIDs'] = name_list 

    return recipes, ingredients

@app.route('/addrecipe')
@app.route('/')
def index(pagetype: str = "ADD_RECIPE"):
    recipes = mongotest.get_all_recipes()

    # Convert Ingredient ID list to Ingredient Names
    for recipe in recipes:
        name_list = []
        id_list = recipe['ingredientIDs']
        for id in id_list:
            name_list.append(mongotest.get_ingredient_name_from_id(id))
        recipe['ingredientIDs'] = name_list 

    return render_template('index.html', recipes=recipes, pagetype=pagetype)

@app.route('/addrecipe', methods=['POST'])
@app.route('/', methods=['POST'])
def add_recipe():
        recipes, ingredients = get_recipes_and_ingredients()

        # Convert Ingredient ID list to Ingredient Names
        for recipe in recipes:
            name_list = []
            id_list = recipe['ingredientIDs']
            for id in id_list:
                name_list.append(mongotest.get_ingredient_name_from_id(id))
            recipe['ingredientIDs'] = name_list

        recipe_name = request.form['RecipeNameText']
        course_name = request.form['CourseNameText']
        ingredients = request.form['IngredientList']
        course_type = mongotest.CourseEnum.BREAKFAST

        if course_name.upper() not in ["BREAKFAST", "LUNCH", "DINNER"]:
            return render_template('index.html', recipes=recipes, show_alert=True, error_message="BADCOURSE", pagetype="ADD_RECIPE")
        elif course_name.upper() in "LUNCH":
            course_type = mongotest.CourseEnum.LUNCH
        elif course_name.upper() in "DINNER":
            course_type = mongotest.CourseEnum.DINNER

        ingredient_list = [ingredient_name.strip() for ingredient_name in ingredients.split(", ")]
        ingredient_limit = sorted([k for k in ingredients], reverse=True)[0]
        if sorted(ingredient_list, reverse=True)[0] > ingredient_limit:
            return render_template('index.html', recipes=recipes, show_alert=True, error_message="TOOHIGHINGREDIENT", pagetype="ADD_RECIPE")
        
        # ingredient_id_list = [mongotest.get_ingredient_id(ingredient) for ingredient in ingredient_list]
        ingredient_id_list = [int(ingredient) for ingredient in ingredient_list]
        mongotest.insert_recipe(recipe_name,course_type,ingredient_id_list)

        return redirect(request.referrer)

@app.route('/delrecipe')
def del_recipe_index():
    return index(pagetype="DEL_RECIPE")


@app.route('/delrecipe', methods=['POST'])
def del_recipe():
    recipes, ingredients = get_recipes_and_ingredients()
    recipe_id = int(request.form['RecipeIDText'])

    if mongotest.get_current_recipe_id() < recipe_id or recipe_id < mongotest.get_smallest_recipe_id():
        return render_template('index.html', recipes=recipes, show_alert=True, error_message="OUTOFRANGERECIPEID", pagetype="DEL_RECIPE")
    
    mongotest.delete_recipe_by_id(recipe_id)
    return redirect(request.referrer)

if __name__ == "__main__":
    app.run(debug=True)

