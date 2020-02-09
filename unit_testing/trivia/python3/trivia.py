#!/usr/bin/env python3

from random import randrange, seed
from player import Player
from questions import Questions
from const import PlayerType


class ConsoleLogger:

    def print(self, message):
        print(message)


class BufferedLogger:
    def __init__(self):
        self.logs = []

    def print(self, message):
        self.logs.append(message)


class Trivia:
    def __init__(self, players_to_create, logger=ConsoleLogger()):
        self.logger = logger
        self.players = []
        self.questions = Questions(logger)
        self.current_player: Player = None
        self.winner: Player = None

        for player in players_to_create:
            if isinstance(player, str):
                self._create_player(player, PlayerType.NORMAL)
            else:
                name, player_type = player
                assert isinstance(name, str)
                assert isinstance(player_type, PlayerType)
                self._create_player(name, player_type)
        self.current_player_index = 0
        self.current_player = self.players[0]

    def _create_player(self, player_name, player_type):
        new_player = Player(player_name, self.logger, player_type)
        self.players.append(new_player)

        self.logger.print(player_name + " was added")
        self.logger.print("They are player number %s" % len(self.players))

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.current_player.name)
        self.logger.print("They have rolled a %s" % roll)

        self.current_player.rolled(roll)

        if self.current_player.in_penalty_box \
                and not self.current_player.is_leaving_penalty_box:
            return None
        
        self.current_player.step(roll)
        return self.questions.ask_next(self.current_player.position)

    def next_player(self):
        self.current_player_index += 1
        if self.current_player_index == len(self.players):
            self.current_player_index = 0
        self.current_player = self.players[self.current_player_index]

    def handle_player(self, first_roll, second_roll):
        question = self.roll(first_roll)

        if question:
            if second_roll == 7:
                self.current_player.wrong_answer(question)
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

    game = Trivia(['Chet', 'Pat', 'Sue', ('Kid1', PlayerType.KID), ('Kid2', PlayerType.KID)])

    game.play(101)
