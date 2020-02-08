#!/usr/bin/env python3

from random import randrange, seed

class ConsoleLogger:

    def print(self, message):
        print(message)

class BufferedLogger:
    def __init__(self):
        self.logs = []

    def print(self, message):
        self.logs.append(message)

class Game:
    def __init__(self, players, logger=ConsoleLogger()):
        self.logger = logger
        self.players = []
        self.places = [0] * 6
        self.purses = [0] * 6
        self.in_penalty_box = [0] * 6

        self.pop_questions = []
        self.science_questions = []
        self.sports_questions = []
        self.rock_questions = []

        self.current_player = 0
        self.is_getting_out_of_penalty_box = False

        for player in players:
            self.add(player)

        for i in range(50):
            self.pop_questions.append("Pop Question %s" % i)
            self.science_questions.append("Science Question %s" % i)
            self.sports_questions.append("Sports Question %s" % i)
            self.rock_questions.append(self.create_rock_question(i))

    def create_rock_question(self, index):
        return "Rock Question %s" % index

    def is_playable(self):
        return self.how_many_players >= 2

    def add(self, player_name):
        self.players.append(player_name)
        self.places[self.how_many_players] = 0
        self.purses[self.how_many_players] = 0
        self.in_penalty_box[self.how_many_players] = False

        self.logger.print(player_name + " was added")
        self.logger.print("They are player number %s" % len(self.players))

        return True

    @property
    def how_many_players(self):
        return len(self.players)

    def step_player(self, roll):
        self.places[self.current_player] = self.places[self.current_player] + roll
        if self.places[self.current_player] > 11:
            self.places[self.current_player] = self.places[self.current_player] - 12

        self.logger.print(self.players[self.current_player] + \
                    '\'s new location is ' + \
                    str(self.places[self.current_player]))

    def set_getting_out(self, is_true):
        self.is_getting_out_of_penalty_box = is_true
        is_true_str = '' if is_true else 'not '
        self.logger.print("%s is %sgetting out of the penalty box" % (self.players[self.current_player], is_true_str))

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.players[self.current_player])
        self.logger.print("They have rolled a %s" % roll)

        if self.in_penalty_box[self.current_player]:
            if roll % 2 != 0:
                self.set_getting_out(True)

                self.step_player(roll)

                self._ask_question()
            else:
                self.set_getting_out(False)
        else:
            self.step_player(roll)

            self._ask_question()

    def _ask_question(self):
        self.logger.print("The category is %s" % self._current_category)
        if self._current_category == 'Pop': self.logger.print(self.pop_questions.pop(0))
        if self._current_category == 'Science': self.logger.print(self.science_questions.pop(0))
        if self._current_category == 'Sports': self.logger.print(self.sports_questions.pop(0))
        if self._current_category == 'Rock': self.logger.print(self.rock_questions.pop(0))

    @property
    def _current_category(self):
        if self.places[self.current_player] == 0: return 'Pop'
        if self.places[self.current_player] == 4: return 'Pop'
        if self.places[self.current_player] == 8: return 'Pop'
        if self.places[self.current_player] == 1: return 'Science'
        if self.places[self.current_player] == 5: return 'Science'
        if self.places[self.current_player] == 9: return 'Science'
        if self.places[self.current_player] == 2: return 'Sports'
        if self.places[self.current_player] == 6: return 'Sports'
        if self.places[self.current_player] == 10: return 'Sports'
        return 'Rock'

    def next_player(self):
        self.current_player += 1
        if self.current_player == len(self.players):
            self.current_player = 0

    def correct_answer(self):
        self.logger.print("Answer was correct!!!!")
        self.purses[self.current_player] += 1
        self.logger.print(self.players[self.current_player] + \
            ' now has ' + \
            str(self.purses[self.current_player]) + \
            ' Gold Coins.')

    def was_correctly_answered(self):
        if self.in_penalty_box[self.current_player]:
            if self.is_getting_out_of_penalty_box:
                self.correct_answer()

                winner = self._did_player_win()
                self.next_player()

                return winner
            else:
                self.next_player()
                return True

        else:
            self.correct_answer()

            winner = self._did_player_win()
            self.next_player()

            return winner

    def wrong_answer(self):
        self.logger.print('Question was incorrectly answered')
        self.logger.print(self.players[self.current_player] + " was sent to the penalty box")
        self.in_penalty_box[self.current_player] = True

        self.next_player()
        return True

    def _did_player_win(self):
        return not (self.purses[self.current_player] == 6)

    def play(self, seed_value):

        no_winner = True
        seed(seed_value)

        while no_winner:
            self.roll(randrange(5) + 1)

            if randrange(9) == 7:
                no_winner = self.wrong_answer()
            else:
                no_winner = self.was_correctly_answered()



if __name__ == '__main__':

    game = Game(['Chet', 'Pat', 'Sue'])

    game.play(122342)
