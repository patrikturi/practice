import copy
import sys

class ElvenKitchen:
    
    def __init__(self):
        self.recipes = [3,7]
        self.elf1_pos = 0
        self.elf2_pos = 1

    def makeRecipes(self, count):
        initial_recipes = len(self.recipes)
        while(len(self.recipes) < initial_recipes + count):
            self.makeRecipe()

    def makeRecipesUpTo(self, count):
        while(len(self.recipes) < count):
            self.makeRecipe()

    def makeRecipe(self):
        # Grab next recipes
        self.elf1_pos = self._get_next_work_recipe(self.elf1_pos)
        self.elf2_pos = self._get_next_work_recipe(self.elf2_pos)
        
        # Get rating of new recipe
        newRecipeRating = self.recipes[self.elf1_pos] + self.recipes[self.elf2_pos]
        ratingStr = str(newRecipeRating)
        for ch in ratingStr:
            self.recipes.append(int(ch))

    def _get_next_work_recipe(self, id):
        return (id + self.recipes[id] + 1)%len(self.recipes)

        
        
    def get_next_ten_recipes(self, start):
        # Because makeRecipe() can't make the exact number of recipes, one iteration might result in multiple new recipes
        offset = len(self.recipes) - start
        assert offset >= 0, "offset={}".format(offset)
        initial_recipes = len(self.recipes)
        self.makeRecipes(10-offset)
        # Do not use negative indexes because makeRecipes() might create more recipes than requested
        last_ten = self.recipes[initial_recipes-offset:initial_recipes+10-offset]
        return ''.join(map(str, last_ten))


if __name__ == '__main__':
    cnt = int(sys.argv[1])
    kitchen = ElvenKitchen()
    kitchen.makeRecipesUpTo(cnt)
    last_ten = kitchen.get_next_ten_recipes(cnt)
    print('Next ten recipes after {} recipes: {}'.format(cnt, last_ten))
