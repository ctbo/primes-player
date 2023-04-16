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


class Player(ABC):

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.position = 0

    def __str__(self):
        cards = "no cards"
        if len(self.hand) == 1:
            cards = f"card {self.hand[0].number}"
        else:
            cards = f"cards {' '.join(card.number for card in self.hand)}"
        return f"<Player {self.name} on square {self.position} holding {cards}>"

    def __repr__(self):
        return self.__str__()

    def reveal_card_numbers(self):
        return [card.number for card in self.hand]

    def receive_card(self, card):
        self.hand.append(card)
        self.hand.sort(key=lambda card: (card.number, card.symbol))

    def kick(self):
        self.position = 0

    @abstractmethod
    def make_move(self, opponents):
        """
        Take a list of opponents and return a list of cards to play.
        It's the `Player`'s responsibility to remove the played cards from their hand.
        """
        pass

class Human(Player):

    def make_move(self, opponents):
        print(f"It's your move, {self.name}!")
        print(f"You are on square number {self.position} and have the following cards:")
        print("  ".join(f"{i}: {card}" for i, card in enumerate(self.hand)))
        print("Your opponents are:")
        for opponent in opponents:
            print(opponent)

        while True: # loop until legal move is input
            s = input("Please enter zero or more cards to play, separated by spaces: ")
            try:
                toplay = [int(c) for c in s.split()]
                assert len(toplay) == len(set(toplay)), "Please don't enter duplicate numbers."
                assert all(0 <= i < len(self.hand) for i in toplay), "Invalid card number(s)."
                # TODO: Check if the move is valid
                toplay.sort(reverse=True)
                playing_cards = []
                for i in toplay:
                    playing_cards.append(self.hand.pop(i))
                return playing_cards
            except Exception as e:
                print(e)



class Fool(Player):

    pass

class Game:
    def __init__(self, *players):
        assert len(players) >= 2, "The number of players must be at least 2."

        self.players = [player if isinstance(player, Player) else Human(player) for player in players]
        self.deck = [Card(number, symbol) for number, primes in enumerate(cardPrimes) for symbol in primes]
        random.shuffle(self.deck)

        # deal one card to each player
        for player in self.players:
            player.receive_card(self.deck.pop())

        self.current_player = 0
        self.first_to_pass = None # number of first player to pass in consecutive sequence of passes

if __name__ == '__main__':
    g = Game("Grant", "Harald", "EJ")
    print(g.deck)
    print(g.players)
    g.players[0].make_move(g.players[1:])
