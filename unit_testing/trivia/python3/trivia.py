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
        self.questions = Questions(logger)
        self.last_question = ''

        for player in player_names:
            self.create_player(player)
        self.current_player_index = 0
        self.current_player = self.players[0]

    # FIXME: dead code, kept here to remind me to implement this
    def is_playable(self):
        return len(self.players) >= 2

    def create_player(self, player_name):
        new_player = Player(player_name, self.logger)
        self.players.append(new_player)

        self.logger.print(player_name + " was added")
        self.logger.print("They are player number %s" % len(self.players))

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.current_player.name)
        self.logger.print("They have rolled a %s" % roll)

        self.current_player.rolled(roll)

        if self.current_player.is_leaving_penalty_box:
            self.current_player.step(roll)
            self.last_question = self.questions.ask_next(self.current_player.position)

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def play(self, seed_value):

        winner_found = False
        seed(seed_value)

        while not winner_found:
            self.roll(randrange(5) + 1)

            if randrange(9) == 7:
                self.current_player.wrong_answer()
            else:
                self.current_player.correct_answer()

            winner_found = self.current_player.is_winner
            self.next_player()


if __name__ == '__main__':

    game = Game(['Chet', 'Pat', 'Sue'])

    game.play(122342)
