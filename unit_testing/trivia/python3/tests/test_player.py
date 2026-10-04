import unittest

from const import BOARD_SIZE, COINS_TO_WIN, PlayerType
from trivia import BufferedLogger
from player import Player

PLAYER1_NAME = 'Joe'


class PlayerTests(unittest.TestCase):

    def setUp(self):
        self.logger = BufferedLogger()
        self.player = Player(PLAYER1_NAME, self.logger, PlayerType.NORMAL)

    def test_name(self):
        self.assertEqual(PLAYER1_NAME, self.player.name)

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

    def test_correctAnswer_inPenaltyNotGettingOut_getsNoCoins(self):
        self.player.in_penalty_box = True
        self.player.is_leaving_penalty_box = False
        self.player.correct_answer()
        self.assertEqual(0, self.player.coins)

    def test_correctAnswer_notInPenalty_getsACoin(self):
        self.player.in_penalty_box = False
        self.player.is_leaving_penalty_box = False
        self.player.correct_answer()
        self.assertEqual(1, self.player.coins)

    def test_correctAnswer_inPenaltyIsGettingOut_getsACoin(self):
        self.player.in_penalty_box = True
        self.player.is_leaving_penalty_box = True
        self.player.correct_answer()
        self.assertEqual(1, self.player.coins)

    def test_wrongAnswer_playerSentToPenaltyBox(self):
        self.assertFalse(self.player.in_penalty_box)
        self.player.wrong_answer('Question')
        self.assertTrue(self.player.in_penalty_box)

    def test_playerGetsOutOfPenaltyBox(self):
        # Player in penalty box rolls even and gets out
        self.player.in_penalty_box = True
        self.player.rolled(3)
        self.player.correct_answer()
        self.assertEqual(1, self.player.coins)

        # Player rolls odd but still gets a coin because he is not in the penalty box
        self.player.rolled(2)
        self.player.correct_answer()
        self.assertEqual(2, self.player.coins)

    def test_playerStaysInPenaltyBox(self):
        # Player stays in penalty box because he rolled even and gets no coin
        self.player.in_penalty_box = True
        self.player.rolled(2)
        self.player.correct_answer()
        self.assertEqual(0, self.player.coins)
