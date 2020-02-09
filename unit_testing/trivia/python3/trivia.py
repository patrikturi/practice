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


class Trivia:
    def __init__(self, player_names, logger=ConsoleLogger()):
        self.logger = logger
        self.players = []
        self.questions = Questions(logger)
        self.last_question: str = None
        self.current_player: Player = None
        self.winner: Player = None

        for player in player_names:
            self._create_player(player)
        self.current_player_index = 0
        self.current_player = self.players[0]

    def _create_player(self, player_name):
        new_player = Player(player_name, self.logger)
        self.players.append(new_player)

        self.logger.print(player_name + " was added")
        self.logger.print("They are player number %s" % len(self.players))

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.current_player.name)
        self.logger.print("They have rolled a %s" % roll)

        self.current_player.rolled(roll)

        if not self.current_player.in_penalty_box \
            or self.current_player.is_leaving_penalty_box:
            self.current_player.step(roll)
            self.last_question = self.questions.ask_next(self.current_player.position)
        else:
            self.last_question = None

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def handle_player(self, first_roll, second_roll):
        self.roll(first_roll)

        if self.last_question:
            if second_roll == 7:
                self.current_player.wrong_answer()
            else:
                self.current_player.correct_answer()

        return self.current_player if self.current_player.is_winner else None

    def play(self, seed_value):
        if len(self.players) < 2:
            raise ValueError('Not enough players.')

        seed(seed_value)

        while True:
            self.winner = self.handle_player(randrange(5) + 1, randrange(9))
            if self.winner:
                break
            self.next_player()


if __name__ == '__main__':

    game = Trivia(['Chet', 'Pat', 'Sue'])

    game.play(122342)
