from flask import Flask, request, render_template, redirect
import kipperdb

app = Flask(__name__)

def get_recipes_and_ingredients():
    recipes = kipperdb.get_all_recipes()
    ingredients = kipperdb.get_all_ingredients()
    return recipes, ingredients

@app.route('/index.html')
@app.route('/addrecipe')
@app.route('/')
def index(pagetype: str = "ADD_RECIPE"):
    recipes, ingredients = get_recipes_and_ingredients()

    # Convert Ingredient ID list to Ingredient Names
    for recipe in recipes:
        name_list = []
        id_list = recipe['ingredientIDs']
        for id in id_list:
            print(id)
            name_list.append(kipperdb.get_ingredient_name_from_id(id))
        recipe['ingredientIDs'] = name_list
        print(name_list)
    
    # Convert Recipe ID list to Recipe Names
    for ingredient in ingredients:
        name_list = []
        id_list = ingredient['usedin']
        for id in id_list:
            name_list.append(kipperdb.get_recipe_name_from_id(id))
        ingredient['usedin'] = name_list
    
    return render_template('index.html', recipes=recipes, ingredients=ingredients, pagetype=pagetype)

@app.route('/addrecipe', methods=['POST'])
@app.route('/', methods=['POST'])
def add_recipe():
        recipes, ingredients = get_recipes_and_ingredients()

        # Convert Ingredient ID list to Ingredient Names
        for recipe in recipes:
            name_list = []
            id_list = recipe['ingredientIDs']
            for id in id_list:
                name_list.append(kipperdb.get_ingredient_name_from_id(id))
            recipe['ingredientIDs'] = name_list

        recipe_name = request.form['RecipeNameText']
        course_name = request.form['CourseNameText']
        ingredients = request.form['IngredientList']
        course_type = kipperdb.CourseEnum.BREAKFAST

        if course_name.upper() not in ["BREAKFAST", "LUNCH", "DINNER"]:
            return render_template('index.html', recipes=recipes, show_alert=True, error_message="BADCOURSE", pagetype="ADD_RECIPE",
            ingredients=ingredients)
        elif course_name.upper() in "LUNCH":
            course_type = kipperdb.CourseEnum.LUNCH
        elif course_name.upper() in "DINNER":
            course_type = kipperdb.CourseEnum.DINNER

        ingredient_list = [ingredient_name.strip() for ingredient_name in ingredients.split(", ")]
        ingredient_limit = sorted([k for k in ingredients], reverse=True)[0]
        if sorted(ingredient_list, reverse=True)[0] > ingredient_limit:
            return render_template('index.html', recipes=recipes, show_alert=True, error_message="OUTOFRANGEINGREDIENTID", pagetype="ADD_RECIPE",
            ingredients=ingredients)
        
        # ingredient_id_list = [kipperdb.get_ingredient_id(ingredient) for ingredient in ingredient_list]
        try:
            ingredient_id_list = [int(ingredient) for ingredient in ingredient_list]
            kipperdb.insert_recipe(recipe_name,course_type,ingredient_id_list)
        except ValueError:
            return render_template('index.html', recipes=recipes, show_alert=True, error_message="INVALIDINGREDIENT", pagetype="ADD_RECIPE")

        return redirect(request.referrer)

@app.route('/delrecipe')
def del_recipe_index():
    return index(pagetype="DEL_RECIPE")

@app.route('/delrecipe', methods=['POST'])
def del_recipe():
    recipes = get_recipes_and_ingredients()[0]
    try:
        recipe_id = int(request.form['RecipeIDText'])
    except ValueError:
        return render_template('index.html', recipes=recipes, show_alert=True, error_message="INVALIDRECIPEID", pagetype="DEL_RECIPE")

    if kipperdb.get_current_recipe_id() < recipe_id or recipe_id < kipperdb.get_smallest_recipe_id():
        return render_template('index.html', recipes=recipes, show_alert=True, error_message="OUTOFRANGERECIPEID", pagetype="DEL_RECIPE")
    
    kipperdb.delete_recipe_by_id(recipe_id)
    return redirect(request.referrer)

@app.route('/addingred')
def add_ingred_index():
    return index(pagetype="ADD_INGRED")

@app.route('/addingred', methods=['POST'])
def add_ingred():
    ingredient = request.form['IngredientNameText']
    kipperdb.insert_ingredient(ingredient)
    return redirect(request.referrer)

@app.route('/delingred')
def del_ingred():
    return index(pagetype="DEL_INGRED")

@app.route('/delingred', methods=['POST'])
def del_ingred_index():
    ingredients = get_recipes_and_ingredients()[1]
    try:
        ingredient = int(request.form['IngredientIDText'])
    except ValueError:
        return render_template('index.html', ingredients=ingredients, show_alert=True, pagetype="DEL_INGRED", error_message="TOOHIGHINGREDIENT")

    kipperdb.delete_ingredient_by_id(ingredient)
    return redirect(request.referrer)

@app.route('/login', methods=['POST', 'GET'])
def login_index():
    pass

if __name__ == "__main__":
    app.run(debug=True)

