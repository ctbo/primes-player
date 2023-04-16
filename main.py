# Play the primes game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

import random
from abc import ABC, abstractmethod

cardPrimes = [
    [3, 2, 3, 3, 2, 3, 2, 2, 2],
    [11, 2, 13, 3, 2, 3, 17, 2, 19],
    [23, 2, 29, 3, 2, 3, 2, 2, 2],
    [11, 5, 13, 31, 3, 37, 17, 2, 19],
    [23, 5, 29, 41, 43, 47, 2, 7, 3],
    [11, 5, 13, 53, 3, 59, 17, 7, 19],
    [23, 5, 29, 31, 3, 37, 61, 7, 67],
    [11, 5, 13, 71, 73, 79, 17, 7, 19],
    [23, 5, 29, 41, 43, 47, 83, 7, 89],
    [11, 5, 13, 31, 97, 37, 17, 7, 19]
]

class Card:
    def __init__(self, number, symbol):
        self.number = number
        self.symbol = symbol

    def __str__(self):
        return f"<{self.number} ({self.symbol})>"

    def __repr__(self):
        return self.__str__()

from abc import ABC, abstractmethod


class GameBot(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def make_move(self, game_state):
        """
        This method should take the current game state as an input and return
        the bot's next move based on its implemented strategy.
        """
        pass

    @abstractmethod
    def reset(self):
        """
        This method should reset the bot's internal state, if necessary,
        so it's ready for a new game.
        """
        pass


class Game:
    def __init__(self, players):
        self.players = players
        self.deck = [Card(number, symbol) for number, primes in enumerate(cardPrimes) for symbol in primes]
        random.shuffle(self.deck)


if __name__ == '__main__':
    g = Game(["Grant", "Harald"])
    print(g.deck)
