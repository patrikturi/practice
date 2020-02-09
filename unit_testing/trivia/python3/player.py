from const import COINS_TO_WIN, BOARD_SIZE


class Player:

    def __init__(self, player_name, logger):
        self.name = player_name
        self.logger = logger
        self.position = 0
        self.coins = 0
        self.in_penalty_box = False
        self.is_leaving_penalty_box = False

    @property
    def is_winner(self):
        return self.coins >= COINS_TO_WIN

    def step(self, count):
        self.position += count
        if self.position >= BOARD_SIZE:
            self.position -= BOARD_SIZE

        self.logger.print(self.name + '\'s new location is ' + str(self.position))

    def add_coin(self):
        self.coins += 1
        self.logger.print(self.name + ' now has ' + str(self.coins) + ' Gold Coins.')

    def rolled(self, value):
        if self.in_penalty_box:
            self.is_leaving_penalty_box = value % 2 != 0
            negate = '' if self.is_leaving_penalty_box else 'not '
            self.logger.print("%s is %sgetting out of the penalty box" % (self.name, negate))
        else:
            self.is_leaving_penalty_box = True

    def correct_answer(self):
        if not self.in_penalty_box \
            or self.is_leaving_penalty_box:

            self.logger.print("Answer was correct!!!!")
            self.add_coin()
            self.in_penalty_box = False

    def wrong_answer(self):
        self.logger.print('Question was incorrectly answered')
        self.logger.print(self.name + " was sent to the penalty box")
        self.in_penalty_box = True
