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
        """
        What other players can see.
        :return: The list of numbers on the back of the cards in the hand
        """
        return [card.number for card in self.hand]

    def receive_card(self, card):
        """
        Put a card into the player's hand.
        :param card: a Card object
        :return: None
        """
        self.hand.append(card)
        # always keep your hand in sorted order
        self.hand.sort(key=lambda card: (card.number, card.symbol))

    def set_position(self, position):
        self.position = position

    def move(self, delta):
        self.position += delta
        assert 0 <= self.position <= 100, f"Can't move {self.name} off-board to {self.position}"

    def needed_to_setback(self):
        """
        :return: list of symbols required to set back this player.
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
        or a combination of symbols that setbacks an opponent
        :param opponents: other players
        :return: a list where each element is a tuple of (list of indices into `self.hand`, revealed) where
            revealed is a bool indicating whether to play the cards revealed
        """
        def more(number, j):
            """
            recursive local function for generating all combinations of adding more of the same number
            :param number: The number to add
            :param j: index to start looking
            :return: list of lists of all combinations
            """
            if j >= len(self.hand) or self.hand[j].number != number:
                return [[]]
            else:
                jss = more(number, j+1)
                return [[j]+js for js in jss] + jss

        legal = [([], False)] # passing is always a legal move
        for i in range(len(self.hand)):
            number = self.hand[i].number
            legal += [([i] + js, False) for js in more(number, i+1)]

        def find_setbacks(symbols, i, prev_symbol):
            """
            Local recursive function to find combinations of cards with `symbols`
            :param symbols: The combination of symbols to find
            :param i: minimum index to look at -- only if same as previous symbol
            :param prev_symbol: previous symbol covered
            :return: a list of lists of indices into the current hand
            """
            if not symbols:
                return [[]]
            symbol = symbols[0]
            if symbol != prev_symbol:
                i = 0
            result = []
            for j in range(i, len(self.hand)):
                if self.hand[j].symbol == symbol:
                    result += [[j] + xs for xs in find_setbacks(symbols[1:], j+1, symbol)]
            return result

        for opponent in opponents:
            symbols = opponent.needed_to_setback()
            setbacks = find_setbacks(symbols, 0, None)

            # RULE: can't set back an opponent off the board.
            # So eliminate all setbacks that would do that
            for setback in setbacks:
                if setback: # only consider nonempty sets of cards
                    delta = sum (self.hand[i].number for i in setback)
                    if 0 <= opponent.position - delta:
                        if (setback, True) not in legal:
                            legal.append((setback, True))

        # RULE: Can't move player off the board.
        for i in range(len(legal)-1, -1, -1):
            js, revealed = legal[i]
            delta = sum(self.hand[j].number for j in js)
            symbols = [self.hand[j].symbol for j in js]
            if revealed:
                total_delta = 0
                for opponent in opponents:
                    if opponent.symbols_match(symbols):
                        total_delta += delta # RULE: For each opponent that is set back, move forward
            else:
                total_delta = delta
            if self.position + total_delta > 100:
                legal.pop(i)

        return legal

    def symbols_match(self, symbols):
        """
        :param symbols: a list of prime factors
        :return: True if `symbols` are exactly the prime factors of the current position
        """
        p = self.position
        for n in symbols:
            if p % n:
                return False
            p //= n
        return p == 1

    @abstractmethod
    def play_cards(self, opponents):
        """
        The strategy of the player: Decide which cards to play and whether to reveal them.
        It's the player's responsibility to remove the played cards from their hand.

        :param opponents: A list of Player objects representing the opponents.
        :return: A tuple (`cards`, `revealed`) where `cards` is a list of `Card` objects
            and `revealed` is a Boolean where True means cards are played symbol-side up
        """
        pass


class Human(Player):
    def play_cards(self, opponents):
        print(f"*** {self.name}, it's your move!")
        print(f"You are on square number {self.position} and have the following cards:")
        print(", ".join(str(card) for card in self.hand))
        print("Your opponents are:")
        for opponent in opponents:
            print(opponent)
        legal_moves = self.legal_moves(opponents)
        while True: # loop until legal move is input
            print("Your options are:")
            for (i, (js, revealed)) in enumerate(legal_moves):
                print(f"{i}: {'pass' if not js else 'reveal' if revealed else 'discard'} {' '.join(str(self.hand[j]) for j in js)}")

            s = input("What would you like to do? ")
            if not s:
                s = "0"
            try:
                i = int(s)
                assert i in range(len(legal_moves)), "Invalid option!"
                # remove the played cards from the hand before returning them
                to_play, reversed = legal_moves[i]
                to_play.sort(reverse=True)
                playing_cards = []
                for i in to_play:
                    playing_cards.append(self.hand.pop(i))
                return playing_cards, revealed
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
            cards, revealed = player.play_cards(opponents)
            if len(cards) == 0:
                self.number_of_passes += 1
            else:
                self.number_of_passes = 0
                numbers = [card.number for card in cards]
                delta = sum(numbers)
                symbols = [card.symbol for card in cards]
                can_setback = any(opponent.symbols_match(symbols) for opponent in opponents)

                if revealed:
                    assert can_setback, "Can't reveal cards unless setting back an opponent." # RULE
                    for opponent in opponents:
                        if opponent.symbols_match(symbols):
                            opponent.move(-delta)
                            player.move(delta) # RULE: move forward for each opponent that is set back
                else:
                    assert len(set(numbers)) == 1, "Can't play different numbers unless setting back someone." # RULE
                    player.move(delta)
                if player.position == 100:
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
