import unittest
from mock import Mock

from trivia import Trivia


class TriviaTests(unittest.TestCase):

    def setUp(self):
        self.game = Trivia(['Chet', 'Pat', 'Sue'])

    def test_roll_stepsForwardAndAsksQuestion(self):
        self.assertFalse(self.game.last_question)
        self.game.roll(2)
        self.assertEqual(2, self.game.current_player.position)
        self.assertTrue(self.game.last_question)

    def test_roll_inPenaltyBoxRolledEven_doesNotMoveNorAskQuestion(self):
        self.game.current_player.in_penalty_box = True
        self.game.roll(4)
        self.assertEqual(0, self.game.current_player.position)
        self.assertFalse(self.game.last_question)
        self.assertFalse(self.game.current_player.is_leaving_penalty_box)

    def test_roll_inPenaltyBoxRolledOdd_stepsForwardAndAsksQuestion(self):
        self.assertFalse(self.game.last_question)
        self.game.current_player.in_penalty_box = True
        self.game.roll(3)
        self.assertEqual(3, self.game.current_player.position)
        self.assertTrue(self.game.last_question)
        self.assertTrue(self.game.current_player.is_leaving_penalty_box)

    def test_nextPlayer(self):
        self.assertEqual('Chet', self.game.current_player.name)
        self.game.next_player()
        self.assertEqual('Pat', self.game.current_player.name)
        self.game.next_player()
        self.assertEqual('Sue', self.game.current_player.name)
        self.game.next_player()
        self.assertEqual('Chet', self.game.current_player.name)

    def test_handlePlayer_correctAnswer(self):
        correct_answer = Mock()
        wrong_answer = Mock()
        self.game.current_player.correct_answer = correct_answer
        self.game.current_player.wrong_answer = wrong_answer
        self.game.handle_player(1, 1)
        correct_answer.assert_called()
        wrong_answer.assert_not_called()

        self.game.handle_player(1, 4)
        correct_answer.assert_called()
        wrong_answer.assert_not_called()

        self.game.handle_player(1, 5)
        correct_answer.assert_called()
        wrong_answer.assert_not_called()

        self.game.handle_player(1, 8)
        correct_answer.assert_called()
        wrong_answer.assert_not_called()

    def test_handlePlayer_wrongAnswer(self):
        correct_answer = Mock()
        wrong_answer = Mock()
        self.game.current_player.correct_answer = correct_answer
        self.game.current_player.wrong_answer = wrong_answer
        self.game.handle_player(1, 7)
        correct_answer.assert_not_called()
        wrong_answer.assert_called()

    def test_handlePlayer_notGettingOutOfPenalty_noQuestionAsked(self):
        correct_answer = Mock()
        wrong_answer = Mock()
        self.game.current_player.correct_answer = correct_answer
        self.game.current_player.wrong_answer = wrong_answer
        self.game.current_player.in_penalty_box = True
        self.game.handle_player(2, 1)
        correct_answer.assert_not_called()
        wrong_answer.assert_not_called()

    def test_play_seed5_ChetWins(self):
        self.game.play(5)
        self.assertEqual('Chet', self.game.winner.name)

    def test_play_seed20000_PatWins(self):
        self.game.play(20000)
        self.assertEqual('Pat', self.game.winner.name)

    def test_play_seed95555_PatWins(self):
        self.game.play(20000)
        self.assertEqual('Pat', self.game.winner.name)

    def test_play_seed122342_ChetWins(self):
        self.game.play(122342)
        self.assertEqual('Chet', self.game.winner.name)

    def test_play_notEnoughPlayers(self):
        game = Trivia(['Bob'])
        self.assertRaises(ValueError, game.play, 5)

    def test_play_minPlayers(self):
        game = Trivia(['Bob', 'Jack'])
        game.play(5)
        self.assertEqual('Jack', game.winner.name)
