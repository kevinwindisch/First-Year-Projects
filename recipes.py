

import pickle
import sys

sys.setrecursionlimit(20_000)


def make_recipe_book(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    recipe_dict = {}

    for ingredient in recipes:
        if ingredient[0] == "compound":
            if ingredient[1] not in recipe_dict:
                recipe_dict[ingredient[1]] = [ingredient[2]]
            else:
                recipe_dict[ingredient[1]].append(ingredient[2])

    return recipe_dict


def make_atomic_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    costs_dict = {}

    for ingredient in recipes:
        if ingredient[0] == "atomic":
            costs_dict[ingredient[1]] = ingredient[2]

    return costs_dict


def remove_forbidden(recipe_book, atomic_costs, forbidden):
    if forbidden is not None:
        for ingredient in forbidden:
            try:
                del recipe_book[ingredient]
            except KeyError:
                del atomic_costs[ingredient]


def recipe_cost(recipes, recipe, forbidden=None):
    """
    finds the cost of a recipe
    """
    cost = 0

    for ingredient in recipe:
        try:
            cost += lowest_cost(recipes, ingredient[0], forbidden) * ingredient[1]
        except TypeError:
            return None

    return cost


def lowest_cost(recipes, food_item, forbidden=None):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    recipe_book = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)
    remove_forbidden(recipe_book, atomic_costs, forbidden)

    if food_item in atomic_costs:  # base case for atomic
        return atomic_costs[food_item]

    if food_item not in recipe_book:  # base case if item is forbidden
        return None

    cost_list = [
        recipe_cost(recipes, recipe, forbidden)
        for recipe in recipe_book[food_item]
        if recipe_cost(recipes, recipe, forbidden) is not None
    ]  # find cost of every recipe

    if not cost_list:  # check if recipe can be made
        return None

    return min(cost_list)


def scale_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    scaled_dict = {}

    for ingredient in flat_recipe:
        scaled_dict[ingredient] = flat_recipe[ingredient] * n

    return scaled_dict


def make_grocery_list(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        make_grocery_list([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    grocery_list = {}

    for recipe in flat_recipes:
        for ingredient in recipe:
            if ingredient not in grocery_list:
                grocery_list[ingredient] = recipe[ingredient]
            else:
                grocery_list[ingredient] += recipe[ingredient]

    return grocery_list


def cheapest_flat_recipe(recipes, food_item, forbidden=None):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """
    recipe_book = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)
    remove_forbidden(recipe_book, atomic_costs, forbidden)

    if food_item in atomic_costs:  # atomic base case
        return {food_item: 1}

    if food_item not in recipe_book:  # forbidden base case
        return None

    def cheapest_recipe(recipe_list):
        """
        finds the cheapest recipe in a list of recipes
        returns flat recipe
        """
        costs = [
            recipe_cost(recipes, recipe, forbidden)
            for recipe in recipe_list
            if recipe_cost(recipes, recipe, forbidden) is not None
        ]  # finds all costs of recipes

        if not costs:
            return None

        lowest = min(costs)

        for recipe in recipe_list:  # finds cheapest
            if recipe_cost(recipes, recipe, forbidden) == lowest:
                return recipe

    cheapest = cheapest_recipe(recipe_book[food_item])

    if cheapest is None:
        return None

    grocery_list = []

    for ingredient in cheapest:
        cheap_recipe = cheapest_flat_recipe(
            recipes, ingredient[0], forbidden
        )  # recursively finds cheapest flat recipe for each ingredient
        if cheap_recipe is None:
            return None
        scaled_recipe = scale_recipe(cheap_recipe, ingredient[1])
        grocery_list.append(scaled_recipe)

    return make_grocery_list(grocery_list)


def ingredient_mixes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes make a certain ingredient as part of a recipe, compute all
    combinations of the flat recipes.
    """
    mixed_list = []

    for index in range(len(flat_recipes)):
        if index == 0:
            for ingredient in flat_recipes[
                0
            ]:  # begin by making recipes for each ingredient of the first list
                mixed_list.append(ingredient)
        else:
            new_mixed_list = []
            for recipe in mixed_list:  # iterates through each recipe in mixed list
                for ingredients in flat_recipes[index]:
                    new_recipe = (
                        recipe.copy()
                    )  # creates a copy to avoid manipulating input
                    for ingredient in ingredients:
                        if ingredient not in new_recipe:
                            new_recipe[ingredient] = ingredients[
                                ingredient
                            ]  # adds new ingredient
                        else:
                            new_recipe[ingredient] += ingredients[
                                ingredient
                            ]  # combines ingredients
                    new_mixed_list.append(new_recipe)
            mixed_list = new_mixed_list  # updates mixed list

    return mixed_list


def all_flat_recipes(recipes, food_item, forbidden=None):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    recipe_book = make_recipe_book(recipes)
    atomic_costs = make_atomic_costs(recipes)
    remove_forbidden(recipe_book, atomic_costs, forbidden)

    if food_item in atomic_costs:  # atomic base case
        return [{food_item: 1}]

    if food_item not in recipe_book:  # forbidden base case
        return []

    all_recipes = []
    for recipe in recipe_book[food_item]:
        flat_recipes = []
        for item in recipe:
            not_scaled = all_flat_recipes(
                recipes, item[0], forbidden
            )  # finds a.f.r. for each item in recipe
            scaled = []
            for new_recipe in not_scaled:
                scaled.append(scale_recipe(new_recipe, item[1]))  # scales each item
            flat_recipes.append(scaled)
        all_recipes.extend(
            ingredient_mixes(flat_recipes)
        )  # mixes flat recipes of each item and adds to output

    return all_recipes


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!
    print("output", all_flat_recipes(example_recipes, "burger"))
