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
            cards = f"cards {' '.join(str(card.number) for card in self.hand)}"
        return f"<Player {self.name} on square {self.position} holding {cards}>"

    def __repr__(self):
        return self.__str__()

    def reveal_card_numbers(self):
        return [card.number for card in self.hand]

    def receive_card(self, card):
        self.hand.append(card)
        # always keep your hand in sorted order
        self.hand.sort(key=lambda card: (card.number, card.symbol))

    def set_position(self, position):
        self.position = position

    def needed_to_kick(self):
        """
        :return: list of symbols required to kick this player.
            This is the prime factorisation of the current position.
        """
        primes = []
        pos = self.position
        i = 2
        while pos > 1:
            if pos % i == 0:
                primes.append(i)
                pos //= i
            else:
                i += 1
        return primes

    def legal_moves(self, opponents):
        """
        legal moves are any number of cards with the same number
        or a combination of symbols that kicks an opponent
        :param opponents: other players
        :return: a list where each element is a list of indices into `self.hand`
        """
        def more(number, j):
            if j >= len(self.hand) or self.hand[j].number != number:
                return [[]]
            else:
                jss = more(number, j+1)
                return [[j]+js for js in jss] + jss

        legal = [[]] # passing is always a legal move
        for i in range(len(self.hand)):
            number = self.hand[i].number
            legal += [[i] + js for js in more(number, i+1)]

        def find_kicks(symbols, i, prev_symbol):
            if not symbols:
                return [[]]
            symbol = symbols[0]
            if symbol != prev_symbol:
                i = 0
            result = []
            for j in range(i, len(self.hand)):
                if self.hand[j].symbol == symbol:
                    result += [[j] + xs for xs in find_kicks(symbols[1:], j+1, symbol)]
            return result

        for opponent in opponents:
            symbols = opponent.needed_to_kick()
            kicks = find_kicks(symbols, 0, None)
            print(f"DEBUG: Trying to kick {opponent.name} with symbols {symbols}: {kicks}")
            for kick in kicks:
                if kick not in legal:
                    legal += [kick]

        return legal

    def kick(self, symbols):
        """
        Check if `symbols` are exactly the prime factors of the current position and
        kick the player back to zero if they are
        :param symbols: the list of prime factors
        :return: True if the player has been kicked
        """
        p = self.position
        for n in symbols:
            if p % n:
                return False
            p //= n
        if p != 1:
            return False
        else:
            self.position = 0
            return True

    @abstractmethod
    def play_cards(self, opponents):
        """
        Take a list of opponents and return a list of cards to play.
        It's the `Player`'s responsibility to remove the played cards from their hand.
        """
        pass


class Human(Player):
    def play_cards(self, opponents):
        print(f"*** {self.name}, it's your move!")
        print("Your opponents are:")
        for opponent in opponents:
            print(opponent)
        print(f"You are on square number {self.position} and have the following cards:")
        print("\n".join(f"{i}: {card}" for i, card in enumerate(self.hand)))
        print(f"{self.legal_moves(opponents)=}")
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
            self.draw_for_player(player)

        self.number_of_passes = 0

    def draw_for_player(self, player):
        if self.deck:
            player.receive_card(self.deck.pop())

    def run(self):
        while self.number_of_passes < len(self.players):
            player = self.players[0]
            opponents = self.players[1:]
            cards = player.play_cards(opponents)
            if len(cards) == 0:
                self.number_of_passes += 1
            else:
                self.number_of_passes = 0
                numbers = [card.number for card in cards]
                symbols = [card.symbol for card in cards]
                kicked = False
                for opponent in opponents:
                    if opponent.kick(symbols):
                        kicked = True # kick all opponents; avoid shot-circuit evaluation as in any()
                        print(f"KICKING {opponent.name}")
                assert kicked or len(set(numbers)) == 1, "Can't play different numbers unless kicking someone."
                new_position = player.position + sum(numbers)
                assert 0 <= new_position <= 100, "Can't move off the board."
                player.position = new_position
                if new_position == 100:
                    break

            for _ in range(len(cards)+1):
                self.draw_for_player(player)

            self.players = opponents + [player] # rotate players

    def print_result(self):
        for player in sorted(self.players, key = lambda player: player.position, reverse=True):
            print(player)


if __name__ == '__main__':
    g = Game("Grant", "Harald")
    g.run()
    g.print_result()
