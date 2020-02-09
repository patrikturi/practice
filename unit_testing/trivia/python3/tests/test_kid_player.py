import unittest

from const import BOARD_SIZE, KID_COINS_TO_WIN, PlayerType
from trivia import BufferedLogger
from player import Player

PLAYER2_NAME = 'Kid'


class KidPlayerTests(unittest.TestCase):

    def setUp(self):
        self.logger = BufferedLogger()
        self.kid = Player(PLAYER2_NAME, self.logger, PlayerType.KID)

    def test_isWinner_Kid_equalCoinsReturnsTrue(self):
        self.kid.coins += KID_COINS_TO_WIN
        self.assertTrue(self.kid.is_winner)

    def test_isWinner_Kid_lessCoinsReturnsFalse(self):
        self.kid.coins += KID_COINS_TO_WIN - 1
        self.assertFalse(self.kid.is_winner)

    def test_wrongAnswer_kidNotSentToPenaltyBox(self):
        self.assertFalse(self.kid.in_penalty_box)
        self.kid.wrong_answer('Rock Question 1')
        self.assertFalse(self.kid.in_penalty_box)

    def test_wrongAnswer_kidSentToPenaltyBoxForPopQuestion(self):
        self.assertFalse(self.kid.in_penalty_box)
        self.kid.wrong_answer('Pop Question 3')
        self.assertTrue(self.kid.in_penalty_box)
