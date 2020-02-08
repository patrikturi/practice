import unittest

from const import BOARD_SIZE
from questions import Questions


class QuestionTests(unittest.TestCase):

    def setUp(self):
        self.questions = Questions()

    def test_Category(self):
        self.assertEqual('Pop', Questions.get_category(0))
        self.assertEqual('Pop', Questions.get_category(4))
        self.assertEqual('Pop', Questions.get_category(8))
        self.assertEqual('Science', Questions.get_category(1))
        self.assertEqual('Science', Questions.get_category(5))
        self.assertEqual('Science', Questions.get_category(9))
        self.assertEqual('Sports', Questions.get_category(2))
        self.assertEqual('Sports', Questions.get_category(6))
        self.assertEqual('Sports', Questions.get_category(10))
        self.assertEqual('Rock', Questions.get_category(3))
        self.assertEqual('Rock', Questions.get_category(7))
        self.assertEqual('Rock', Questions.get_category(11))

    def test_CategoryMaxRaisesError(self):
        self.assertRaises(ValueError, lambda: Questions.get_category(BOARD_SIZE))

    def test_CategoryMinRaisesError(self):
        self.assertRaises(ValueError, lambda: Questions.get_category(-1))

    def test_getNextQuestion(self):
        self.assertNextQuestion('Pop', 0)
        self.assertNextQuestion('Pop', 1)
        self.assertNextQuestion('Pop', 2)
        self.assertNextQuestion('Science', 0)
        self.assertNextQuestion('Science', 1)
        self.assertNextQuestion('Science', 2)
        self.assertNextQuestion('Sports', 0)
        self.assertNextQuestion('Sports', 1)
        self.assertNextQuestion('Sports', 2)
        self.assertNextQuestion('Rock', 0)
        self.assertNextQuestion('Rock', 1)
        self.assertNextQuestion('Rock', 2)

    def assertNextQuestion(self, category, index):
        self.assertEqual(f'{category} Question {index}', self.questions.get_next(category))
