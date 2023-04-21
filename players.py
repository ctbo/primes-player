# Play the primes game
# This module contains various players that can play the game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

import random
from abc import ABC, abstractmethod
import tkinter as tk

import os
import platform


def clear_screen():
    if platform.system().lower() == "windows":
        os.system("cls")
    else:
        os.system("clear")

from carddict import *

class Card:
    def __init__(self, number, symbol):
        self.number = number
        self.symbol = symbol

    def __str__(self):
        return f"<{self.number} ({self.symbol})>"

    def __repr__(self):
        return self.__str__()

from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GUIState:
    opponent_string: str
    opponent_hand: List[Card]
    player_string: str
    player_hand: List[Card]
    legal_moves: List[Tuple[List[Card], bool]]


class CardGameGUI:
    def __init__(self, master, input_queue, output_queue):
        self.master = master
        self.master.title("Card Game")
        self.input_queue = input_queue
        self.output_queue = output_queue

        self.card_images_folder = 'resources'
        self.card_backs = [f"{i}" for i in cardDict.keys()]
        self.card_fronts = [f"{number}({symbol})" for number, symbols in cardDict.items() for symbol in symbols]
        self.hand = random.sample(self.card_fronts, 5)
        self.opponent_hand = random.sample(self.card_backs, 5)
        self.selected_cards = []
        self.legal_moves = []

        self.load_card_images()
        self.create_widgets()

    def load_card_images(self):
        self.card_image_objects = {}
        for card in self.card_backs + self.card_fronts:
            image_path = os.path.join(self.card_images_folder, f"{card}.png")
            self.card_image_objects[card] = tk.PhotoImage(file=image_path)

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill='both', expand=True)

        self.left_frame = tk.Frame(self.main_frame)
        self.left_frame.grid(row=0, column=0, sticky='nsew')

        self.label_opponent = tk.Label(self.left_frame, text="Opponent's cards:")
        self.label_opponent.pack(pady=5)

        self.opponent_cards_frame = tk.Frame(self.left_frame)
        self.opponent_cards_frame.pack(pady=5)

        self.opponent_card_labels = []

        self.label_player = tk.Label(self.left_frame, text="Your cards:")
        self.label_player.pack(pady=5)

        self.cards_frame = tk.Frame(self.left_frame)
        self.cards_frame.pack(pady=5)

        self.card_checkbuttons = []

        self.play_button = tk.Button(self.left_frame, text="Play selected cards", command=self.play_cards)
        self.play_button.pack(pady=5)

        self.reveal_button = tk.Button(self.left_frame, text="Play selected card revealed", command=self.reveal_cards)
        self.reveal_button.pack(pady=5)

        # self.quit_button = tk.Button(self.left_frame, text="Quit", command=self.master.quit)
        # self.quit_button.pack(pady=5)

        self.right_frame = tk.Frame(self.main_frame)
        self.right_frame.grid(row=0, column=1, sticky='nsew')

        self.log_label = tk.Label(self.right_frame, text="Game Log:")
        self.log_label.pack(pady=5)

        self.scrollbar = tk.Scrollbar(self.right_frame)
        self.scrollbar.pack(side='right', fill='y')

        self.log_text = tk.Text(self.right_frame, wrap='word', yscrollcommand=self.scrollbar.set)
        self.log_text.pack(expand=True, fill='both')
        self.scrollbar.config(command=self.log_text.yview)

        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def create_opponent_cards(self, opponent_cards):
        self.opponent_card_labels = []
        for card in opponent_cards:
            card_label = tk.Label(self.opponent_cards_frame, image=self.card_image_objects[f"{card.number}"])
            card_label.pack(side='left')
            self.opponent_card_labels.append(card_label)

    def create_player_cards(self, player_cards):
        self.hand = player_cards
        self.card_vars = [tk.BooleanVar() for _ in self.hand]

        self.card_checkbuttons = []
        for i, card in enumerate(player_cards):
            card_frame = tk.Frame(self.cards_frame)
            card_frame.pack(side='left')

            card_label = tk.Label(card_frame, image=self.card_image_objects[f"{card.number}({card.symbol})"])
            card_label.pack()

            check_button = tk.Checkbutton(card_frame, variable=self.card_vars[i],
                                          onvalue=True, offvalue=False,
                                          command=self.update_selected_cards)
            check_button.pack()
            self.card_checkbuttons.append(check_button)

    def update_selected_cards(self):
        self.selected_cards = [card for card, var in zip(self.hand, self.card_vars) if var.get()]
        if (self.selected_cards, False) in self.legal_moves:
            self.play_button.config(state=tk.NORMAL)
        else:
            self.play_button.config(state=tk.DISABLED)
        if (self.selected_cards, True) in self.legal_moves:
            self.reveal_button.config(state=tk.NORMAL)
        else:
            self.reveal_button.config(state=tk.DISABLED)


    def play_cards(self):
        self.input_queue.put_nowait((self.selected_cards, False))
        # self.log_message(f"You played: {', '.join(self.selected_cards)}")

    def reveal_cards(self):
        self.input_queue.put_nowait((self.selected_cards, True))

    def update_GUI_state(self, state):
        self.legal_moves = state.legal_moves
        self.label_opponent['text'] = state.opponent_string
        self.label_player['text'] = state.player_string

        # Clear the current card labels and checkbuttons
        for card_label in self.opponent_card_labels:
            card_label.destroy()
        for check_button in self.card_checkbuttons:
            check_button.master.destroy()

        # Create the new card labels and checkbuttons for the updated hands
        self.create_opponent_cards(state.opponent_hand)
        self.create_player_cards(state.player_hand)

        self.update_selected_cards()

    def log_message(self, message):
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message+'\n')
        self.log_text.configure(state='disabled')
        self.log_text.see(tk.END)

    async def receive_messages(self):
        while True:
            message = await self.output_queue.get()
            if isinstance(message, GUIState):
                self.update_GUI_state(message)
            else:
                self.log_message(message)


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
    async def _choose_cards_to_play(self, opponents):
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
            or just the number if the card has been played unrevealed.
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

    def position_with_hints(self):
        """
        Format the current position with prime factors for text mode play.
        :return: formatted string to print the current position
        """
        nds = self.needed_to_setback()
        result = str(self.position)
        if len(nds) > 1:
            result += f" = {' * '.join(str(p) for p in nds)}"
        return result

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

    async def play_cards(self, opponents):
        playing_cards, revealed = await self._choose_cards_to_play(opponents)
        for card in playing_cards:
            self.hand.remove(card)
        return playing_cards, revealed


class Human(Player):

    def _default_name(self):
        return "Human"

    async def _choose_cards_to_play(self, opponents):
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
                print(f"""{i}: {'pass' if not cards else 'play revealed' if revealed else 'play'} {
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


class GUI(Player):
    def __init__(self):
        super().__init__()
        self.input_queue = None
        self.output_queue = None

    def connect_queues(self, input_queue, output_queue):
        self.input_queue = input_queue
        self.output_queue = output_queue

    def _default_name(self) -> str:
        return "You"

    async def _choose_cards_to_play(self, opponents):
        assert len(opponents) == 1
        opponent = opponents[0]
        gui_state = GUIState(f"{opponent.name} on square {opponent.position_with_hints()}",
                             opponent.hand,
                             f"You are on square {self.position_with_hints()}",
                             self.hand,
                             self.legal_moves(opponents)
                             )
        self.output_queue.put_nowait(gui_state)
        self.output_queue.put_nowait("Hint: your options are:")
        for cards, revealed in self.legal_moves(opponents):
            self.output_queue.put_nowait(f"""- {'pass' if not cards else 'play revealed' if revealed else 'play'} {
            ' '.join(str(card) for card in cards)}""")

        cards_to_play, revealed = await self.input_queue.get()
        if revealed:
            self.output_queue.put_nowait(f"You reveal {' '.join(str(card) for card in cards_to_play)}")
        else:
            self.output_queue.put_nowait(f"You play {' '.join(str(card) for card in cards_to_play)}")

        return cards_to_play, revealed


    def receive_information(self, opponent, cards_played):
        self.output_queue.put_nowait(f"""{opponent.name} plays {
            ' '.join(str(card) for card in cards_played) if cards_played else 'pass'}""")


class RandomBot(Player):
    """
    Select a legal move at random.
    """
    def _default_name(self):
        return "RandomBot"

    async def _choose_cards_to_play(self, opponents):
        return random.choice(self.legal_moves(opponents))

    def receive_information(self, opponent, cards_played):
        pass


class RandomNoPassBot(Player):
    """
    Select a legal move at random, but don't pass unless that's the only legal move.
    """
    def _default_name(self):
        return "RandomNoPassBot"

    async def _choose_cards_to_play(self, opponents):
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

    async def _choose_cards_to_play(self, opponents):
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

    async def _choose_cards_to_play(self, opponents):
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

    async def _choose_cards_to_play(self, opponents):
        l = self.legal_moves(opponents)

        return max(l, key = lambda m: (m[1], sum(card.number for card in m[0])))

    def receive_information(self, opponent, cards_played):
        pass


