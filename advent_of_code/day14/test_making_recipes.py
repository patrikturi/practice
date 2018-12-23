import unittest
from elven_kitchen import ElvenKitchen

class TestMakingRecpies(unittest.TestCase):

    def test_table(self):
        kitchen = ElvenKitchen()
        kitchen.makeRecipes(1)
        self.assertEqual([3,7,1,0], kitchen.recipes)
        kitchen.makeRecipes(1)
        self.assertEqual([3,7,1,0,1,0], kitchen.recipes)
        kitchen.makeRecipes(1)
        self.assertEqual([3,7,1,0,1,0,1], kitchen.recipes)

        kitchen.makeRecipes(13)
        self.assertEqual([3, 7, 1, 0, 1, 0, 1, 2, 4, 5, 1, 5, 8, 9, 1, 6, 7, 7, 9, 2], kitchen.recipes)

    def test_up_to5(self):
        kitchen = ElvenKitchen()
        kitchen.makeRecipesUpTo(5)
        self.assertEqual('0124515891', kitchen.get_next_ten_recipes(5))

    def test_up_to9(self):
        kitchen2 = ElvenKitchen()
        kitchen2.makeRecipesUpTo(9)
        self.assertEqual('5158916779', kitchen2.get_next_ten_recipes(9))

    def test_up_to18(self):
        kitchen3 = ElvenKitchen()
        kitchen3.makeRecipesUpTo(18)
        self.assertEqual('9251071085', kitchen3.get_next_ten_recipes(18))

    def test_up_to2018(self):
        kitchen3 = ElvenKitchen()
        kitchen3.makeRecipesUpTo(2018)
        self.assertEqual('5941429882', kitchen3.get_next_ten_recipes(2018))
