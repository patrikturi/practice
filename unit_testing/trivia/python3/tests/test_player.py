import unittest

from const import BOARD_SIZE, COINS_TO_WIN
from trivia import BufferedLogger
from player import Player

PLAYER_NAME = 'Joe'


class PlayerTests(unittest.TestCase):

    def setUp(self):
        self.logger = BufferedLogger()
        self.player = Player(PLAYER_NAME, self.logger)

    def test_name(self):
        self.assertEqual(PLAYER_NAME, self.player.name)

    def test_stepSingle(self):
        self.player.step(2)
        self.assertEqual(2, self.player.position)

    def test_stepBoardSize(self):
        self.player.step(BOARD_SIZE)
        self.assertEqual(0, self.player.position)

    def test_stepMultiple(self):
        self.player.step(2)
        self.player.step(3)
        self.assertEqual(5, self.player.position)

    def test_stepRollOver(self):
        self.player.step(BOARD_SIZE+3)
        self.assertEqual(3, self.player.position)

    def test_isWinner_lessCoinsReturnsFalse(self):
        self.player.coins += COINS_TO_WIN - 1
        self.assertFalse(self.player.is_winner)

    def test_isWinner_equalCoinsReturnsTrue(self):
        self.player.coins += COINS_TO_WIN
        self.assertTrue(self.player.is_winner)

    def test_isWinner_moreCoinsReturnsTrue(self):
        self.player.coins += COINS_TO_WIN + 1
        self.assertTrue(self.player.is_winner)
