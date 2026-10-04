
from const import BOARD_SIZE
from collections import defaultdict

class Questions:

    CATEGORIES = ['Pop', 'Science', 'Sports', 'Rock']

    def __init__(self, logger):
        self.logger = logger
        self._questions = defaultdict(list)

        for i in range(50):
            for category in self.CATEGORIES:
                self._questions[category].append(f"{category} Question {i}")     

    def get_next(self, category):
        return self._questions[category].pop(0)

    @classmethod
    def get_category(cls, position):
        if position >= BOARD_SIZE or position < 0:
            raise ValueError()

        category_index = position % len(cls.CATEGORIES)
        return cls.CATEGORIES[category_index]

    def ask_next(self, position):
        current_category = self.get_category(position)
        self.logger.print("The category is %s" % current_category)
        current_question = self.get_next(current_category)

        self.logger.print(current_question)
        return current_question
