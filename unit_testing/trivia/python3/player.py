from const import COINS_TO_WIN, BOARD_SIZE


class Player:

    def __init__(self, player_name, logger):
        self.name = player_name
        self.logger = logger
        self.position = 0
        self.coins = 0
        self.in_penalty_box = False

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
