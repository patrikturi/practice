#!/usr/bin/env python3

from random import randrange, seed
from player import Player


class ConsoleLogger:

    def print(self, message):
        print(message)


class BufferedLogger:
    def __init__(self):
        self.logs = []

    def print(self, message):
        self.logs.append(message)


class Game:
    def __init__(self, player_names, logger=ConsoleLogger()):
        self.logger = logger
        self.players = []

        self.pop_questions = []
        self.science_questions = []
        self.sports_questions = []
        self.rock_questions = []

        self.is_getting_out_of_penalty_box = False

        for player in player_names:
            self.add(player)
        self.current_player_index = 0
        self.current_player = self.players[0]

        for i in range(50):
            self.pop_questions.append("Pop Question %s" % i)
            self.science_questions.append("Science Question %s" % i)
            self.sports_questions.append("Sports Question %s" % i)
            self.rock_questions.append("Rock Question %s" % i)

    def is_playable(self):
        return len(self.players) >= 2

    def add(self, player_name):
        new_player = Player(player_name, self.logger)
        self.players.append(new_player)

        self.logger.print(player_name + " was added")
        self.logger.print("They are player number %s" % len(self.players))

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.current_player.name)
        self.logger.print("They have rolled a %s" % roll)

        if self.current_player.in_penalty_box:
            self.is_getting_out_of_penalty_box = roll % 2 != 0
            negate = '' if self.is_getting_out_of_penalty_box else 'not '
            self.logger.print("%s is %sgetting out of the penalty box" % (self.current_player.name, negate))

            if not self.is_getting_out_of_penalty_box:
                return

        self.current_player.step(roll)

        self._ask_question()

    def _ask_question(self):
        self.logger.print("The category is %s" % self._current_category)
        if self._current_category == 'Pop': 
            questions = self.pop_questions
        if self._current_category == 'Science':
            questions = self.science_questions
        if self._current_category == 'Sports':
            questions = self.sports_questions
        if self._current_category == 'Rock':
            questions = self.rock_questions

        self.logger.print(questions.pop(0))

    @property
    def _current_category(self):
        position = self.current_player.position
        if position == 0: return 'Pop'
        if position == 4: return 'Pop'
        if position == 8: return 'Pop'
        if position == 1: return 'Science'
        if position == 5: return 'Science'
        if position == 9: return 'Science'
        if position == 2: return 'Sports'
        if position == 6: return 'Sports'
        if position == 10: return 'Sports'
        return 'Rock'

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def correct_answer(self):
        self.logger.print("Answer was correct!!!!")
        self.current_player.add_coin()

    def was_correctly_answered(self):
        if self.current_player.in_penalty_box \
            and not self.is_getting_out_of_penalty_box:

            return False

        self.correct_answer()

        return self.current_player.is_winner

    def wrong_answer(self):
        self.logger.print('Question was incorrectly answered')
        self.logger.print(self.current_player.name + " was sent to the penalty box")
        self.current_player.in_penalty_box = True

        self.next_player()

    def play(self, seed_value):

        winner_found = False
        seed(seed_value)

        while not winner_found:
            self.roll(randrange(5) + 1)

            if randrange(9) == 7:
                self.wrong_answer()
            else:
                winner_found = self.was_correctly_answered()
                self.next_player()


if __name__ == '__main__':

    game = Game(['Chet', 'Pat', 'Sue'])

    game.play(122342)
