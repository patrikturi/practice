from const import COINS_TO_WIN, KID_COINS_TO_WIN, BOARD_SIZE, PlayerType


class Player:

    def __init__(self, player_name, logger, player_type=PlayerType.NORMAL):
        self.name = player_name
        self.type = player_type
        self.logger = logger
        self.position = 0
        self.coins = 0
        self.in_penalty_box = False
        self.is_leaving_penalty_box = False

    @property
    def is_winner(self):
        coins_required = KID_COINS_TO_WIN if self.type == PlayerType.KID else COINS_TO_WIN
        return self.coins >= coins_required

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

    def wrong_answer(self, question):
        self.logger.print('Question was incorrectly answered')
        
        category = question.split(' ')[0]
        if self.type != PlayerType.KID or category.lower() == 'pop':
            self.logger.print(self.name + " was sent to the penalty box")
            self.in_penalty_box = True
