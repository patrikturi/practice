#!/usr/bin/env python3

from random import randrange, seed
from player import Player
from questions import Questions


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

        self.questions = Questions()

        # FIXME: this should be a property of the Player
        self.is_getting_out_of_penalty_box = False

        for player in player_names:
            self.add(player)
        self.current_player_index = 0
        self.current_player = self.players[0]

    # FIXME: dead code, kept here to remind me to implement this
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

        self.ask_question(self.current_player.position)

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def ask_question(self, position):
        current_category = self.questions.get_category(position)
        self.logger.print("The category is %s" % current_category)
        current_question = self.questions.get_next(current_category)

        self.logger.print(current_question)

    def correct_answer(self):
        self.logger.print("Answer was correct!!!!")
        self.current_player.add_coin()

    def was_correctly_answered(self):
        # FIXME: currently in_penalty_box is never reset to False
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
