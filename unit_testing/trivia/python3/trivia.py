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
            self.rock_questions.append("Rock Question %s" % i)

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

    def roll(self, roll):
        self.logger.print("%s is the current player" % self.players[self.current_player])
        self.logger.print("They have rolled a %s" % roll)

        if self.in_penalty_box[self.current_player]:
            self.is_getting_out_of_penalty_box = roll % 2 != 0
            negate = '' if self.is_getting_out_of_penalty_box else 'not '
            self.logger.print("%s is %sgetting out of the penalty box" % (self.players[self.current_player], negate))

            if not self.is_getting_out_of_penalty_box:
                return

        self.step_player(roll)

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
        position = self.places[self.current_player]
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
        if self.in_penalty_box[self.current_player] \
            and not self.is_getting_out_of_penalty_box:

            self.next_player()
            return False

        self.correct_answer()

        winner = self._did_player_win()
        self.next_player()

        return winner

    def wrong_answer(self):
        self.logger.print('Question was incorrectly answered')
        self.logger.print(self.players[self.current_player] + " was sent to the penalty box")
        self.in_penalty_box[self.current_player] = True

        self.next_player()

    def _did_player_win(self):
        return self.purses[self.current_player] == 6

    def play(self, seed_value):

        winner_found = False
        seed(seed_value)

        while not winner_found:
            self.roll(randrange(5) + 1)

            if randrange(9) == 7:
                self.wrong_answer()
            else:
                winner_found = self.was_correctly_answered()


if __name__ == '__main__':

    game = Game(['Chet', 'Pat', 'Sue'])

    game.play(122342)
