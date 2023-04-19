# Play the primes game
# This module contains various players that can play the game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

import random
from abc import ABC, abstractmethod


class Player(ABC):
    assigned_names = set()
    def __init__(self, base_name=None):
        if base_name is None:
            base_name = self._default_name()
        self.name = base_name
        i = 1
        while self.name in Player.assigned_names:
            i += 1
            self.name = f"{base_name}{i}"
        Player.assigned_names.add(self.name)
        self.reset()

    @abstractmethod
    def _default_name(self) -> str:
        """
        :return: A default name prefix for a player of this class.
        """

    @abstractmethod
    def _choose_cards_to_play(self, opponents):
        """
        The strategy of the player: Decide which cards to play and whether to reveal them.
        :param opponents: A list of Player objects representing the opponents.
        :return: A tuple (`cards`, `revealed`) where `cards` is a list Card objects to be played
            and `revealed` is a Boolean where True means cards are played symbol-side up
        """

    @abstractmethod
    def receive_information(self, opponent, cards_played):
        """
        Receive information about other player's actions.
        :param opponent: The Player who played the action
        :param cards_played: A list of mixed types: Either a Card object if the card has been revealed
            or just the number if the card has been discarded.
        :return: None
        """

    def reset(self):
        """
        Reset internal state of player for a new game. Subclasses should override this if they have more internal state
        :return: None
        """
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
        :return: a list where each element is a tuple of (list of Card objects, revealed) where
            revealed is a bool indicating whether to play the cards revealed. Passing is always first in the list.
        """
        def more(number, j):
            """
            recursive local function for generating all combinations of adding more of the same number
            :param number: The number to add
            :param j: index to start looking
            :return: list of lists of all combinations (indices into self.hand)
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

        # replace indices by actual card objects
        legal_cards = [([self.hand[j] for j in js], revealed) for js, revealed in legal]

        return legal_cards

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

    def play_cards(self, opponents):
        playing_cards, revealed = self._choose_cards_to_play(opponents)
        for card in playing_cards:
            self.hand.remove(card)
        return playing_cards, revealed


class Human(Player):

    def _default_name(self):
        return "Human"

    def _choose_cards_to_play(self, opponents):
        input(f"*** {self.name}, it's your move. Press Enter to look at your cards! ")
        print(f"You are on square number {self.position} and have the following cards:")
        print(", ".join(str(card) for card in self.hand))
        print("Your opponents are:")
        for opponent in opponents:
            print(opponent)
        legal_moves = self.legal_moves(opponents)
        while True: # loop until legal move is input
            print("Your options are:")
            for (i, (cards, revealed)) in enumerate(legal_moves):
                print(f"""{i}: {'pass' if not cards else 'reveal' if revealed else 'discard'} {
                    ' '.join(str(card) for card in cards)}""")

            s = input("What would you like to do? ")
            if not s:
                s = "0"
            try:
                i = int(s)
                assert i in range(len(legal_moves)), "Invalid option!"
                clear_screen()
                return legal_moves[i]
            except Exception as e:
                print(e)

    def receive_information(self, opponent, cards_played):
        print(f"""{self.name}, take note that {opponent.name} has just played {
            ' '.join(str(card) for card in cards_played) if cards_played else 'pass'}""")


class RandomBot(Player):
    """
    Select a legal move at random.
    """
    def _default_name(self):
        return "RandomBot"

    def _choose_cards_to_play(self, opponents):
        return random.choice(self.legal_moves(opponents))

    def receive_information(self, opponent, cards_played):
        pass


class RandomNoPassBot(Player):
    """
    Select a legal move at random, but don't pass unless that's the only legal move.
    """
    def _default_name(self):
        return "RandomNoPassBot"

    def _choose_cards_to_play(self, opponents):
        l = self.legal_moves(opponents)
        if len(l) == 1:
            return l[0]
        return random.choice(l[1:])

    def receive_information(self, opponent, cards_played):
        pass


class RandomTortoise(Player):
    """
    Pass if we're ahead, otherwise pick a random non-passing move
    """
    def _default_name(self) -> str:
        return "RandomTortoise"

    def _choose_cards_to_play(self, opponents):
        l = self.legal_moves(opponents)
        if len(l) == 1 or all(self.position > opponent.position for opponent in opponents):
            return l[0]
        return random.choice(l[1:])

    def receive_information(self, opponent, cards_played):
        pass


class GreedyTortoise(Player):
    """
    Pass if we're ahead, otherwise pick the largest revealed move or the largest unrevealed move
    """
    def _default_name(self) -> str:
        return "GreedyTortoise"

    def _choose_cards_to_play(self, opponents):
        l = self.legal_moves(opponents)
        if len(l) == 1 or all(self.position > opponent.position for opponent in opponents):
            return l[0]

        return max(l[1:], key = lambda m: (m[1], sum(card.number for card in m[0])))

    def receive_information(self, opponent, cards_played):
        pass


class Forrest(Player):
    """
    Pick the largest revealed move or the largest unrevealed move
    """
    def _default_name(self) -> str:
        return "Forrest"

    def _choose_cards_to_play(self, opponents):
        l = self.legal_moves(opponents)

        return max(l, key = lambda m: (m[1], sum(card.number for card in m[0])))

    def receive_information(self, opponent, cards_played):
        pass


