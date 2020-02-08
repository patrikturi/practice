import unittest

from trivia import Game, BufferedLogger


def get_refs(seed_value):
    with open(f'tests/references/seed{seed_value}.txt', 'r') as file:
        return file.read().split('\n')


class GameReferenceTests(unittest.TestCase):

    def setUp(self):
        self.logger = BufferedLogger()
        self.game = Game(self.logger)
        self.game.add('Chet')
        self.game.add('Pat')
        self.game.add('Sue')

    def test_seed5(self):
        self.game.play(5)
        self.assertEqual(get_refs(5), self.logger.logs)

    def test_seed20000(self):
        self.game.play(20000)
        self.assertEqual(get_refs(20000), self.logger.logs)

    def test_seed95555(self):
        self.game.play(95555)
        self.assertEqual(get_refs(95555), self.logger.logs)

    def test_seed122342(self):
        self.game.play(122342)
        self.assertEqual(get_refs(122342), self.logger.logs)
