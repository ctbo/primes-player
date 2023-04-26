# Play the primes game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

import asyncio

from players import *
from carddict import cardDict


class Game:
    def __init__(self, *players):
        assert len(players) >= 2, "The number of players must be at least 2."

        self.verbose = False
        # self.players = [player if isinstance(player, Player) else Human(player) for player in players]
        self.players = []
        self.human_present = False
        self.GUI_player = None
        for player in players:
            if not isinstance(player, Player):
                player = Human(player)
            if isinstance(player, Human):
                assert not self.GUI_player, "Can't combine GUI with text mode Human."
                self.human_present = True
            if isinstance(player, GUI):
                assert not self.GUI_player, "Only one player per game can have a GUI."
                assert not self.human_present, "Can't combine GUI with text mode Human."
                self.GUI_player = player
            self.players.append(player)

        self.input_queue = None
        self.output_queue = None
        self.should_exit = False
        if self.GUI_player:
            assert len(self.players) == 2, "GUI presently only supports exactly one opponent."
            self.input_queue = asyncio.Queue()
            self.output_queue = asyncio.Queue()
            self.GUI_player.connect_queues(self.input_queue, self.output_queue)

        self.deck = [Card(number, symbol) for number, primes in cardDict.items() for symbol in primes]
        random.shuffle(self.deck)

        self.number_of_setbacks = 0
        self.number_of_turns = 0

        if self.human_present:
            print(f"Version: {VERSION}")

    def _draw_for_player(self, player):
        """
        Draw a card if the deck is nonempty.
        :param player: The player who gets the card
        :return: True if a card was drawn
        """
        if self.deck:
            player.receive_card(self.deck.pop())
            return True
        return False

    def set_verbose(self, verbose):
        self.verbose = verbose

    def run(self):
        """
        Play the game until one player wins or all players pass. Leaves `self.players` sorted by winner.
        :return: None
        """
        if not self.GUI_player:
            asyncio.run(self.gameplay())
        else:
            asyncio.run(self.gui_gameplay())

    async def gui_gameplay(self):
        root = tk.Tk()
        gui = CardGameGUI(root, self.input_queue, self.output_queue)

        def on_closing():
            self.should_exit = True

        root.protocol("WM_DELETE_WINDOW", on_closing)

        gameplay_task = asyncio.create_task(self.gameplay())
        message_task = asyncio.create_task(gui.receive_messages())

        async def tk_event_loop():
            while not self.should_exit:
                root.update()
                await asyncio.sleep(0.05)

        await tk_event_loop()

        gameplay_task.cancel()
        message_task.cancel()
        root.destroy()

    def inform_about_top_of_deck(self, player):
        if self.deck:
            player.receive_information(TopOfDeckInfo(self.deck[-1].number))
        else:
            player.receive_information(TopOfDeckInfo(None))

    async def gameplay(self):
        for player in self.players:
            player.reset()
        # deal one card to each player
        for player in self.players:
            self._draw_for_player(player)
        self.number_of_passes = 0
        continue_move = False
        all_cards_played = []

        for player in self.players:
            self.inform_about_top_of_deck(player)

        while self.number_of_passes < len(self.players):
            if not continue_move:
                all_cards_played = []
                self.number_of_turns += 1

            player = self.players[0]
            opponents = self.players[1:]
            if self.verbose:
                print(f"{player} to play.")
            cards, revealed = await player.play_cards(opponents)
            cards_played = []
            if len(cards) == 0:
                if self.verbose:
                    print(f"{player.name} passes.")
                if not continue_move:
                    self.number_of_passes += 1
                continue_move = False
            else:
                self.number_of_passes = 0
                numbers = [card.number for card in cards]
                delta = sum(numbers)
                symbols = [card.symbol for card in cards]
                can_setback = any(opponent.symbols_match(symbols) for opponent in opponents)

                if revealed:
                    assert can_setback, "Can't reveal cards unless setting back an opponent."  # RULE
                    for opponent in opponents:
                        if opponent.symbols_match(symbols):
                            opponent.move(-delta)
                            player.move(delta)  # RULE: move forward for each opponent that is set back
                            self.number_of_setbacks += 1
                    cards_played = cards
                    continue_move = True
                else:
                    assert len(set(numbers)) == 1, "Can't play different numbers unless setting back someone."  # RULE
                    player.move(delta)
                    cards_played = [card.number for card in cards]
                    continue_move = False
                all_cards_played += cards_played
                if self.verbose:
                    print(f"{player.name} plays {' '.join(str(card) for card in cards_played)}")

            for opponent in opponents:
                opponent.receive_information(CardsPlayedInfo(player, cards_played))

            if player.position == 100:
                break

            # RULE: If a player reveals cards, they can continue their move.
            # If they don't, they draw new cards and it's the next player's turn.
            if not continue_move:

                for _ in range(len(all_cards_played) + 1):  # RULE: draw one more card than played
                    if self._draw_for_player(player):
                        for opponent in opponents:
                            opponent.receive_information(CardDrawInfo(player))

                for p in self.players:
                    self.inform_about_top_of_deck(p)

                self.players = opponents + [player]  # rotate players

        # game over.
        for player in self.players:
            player.receive_information(GameOverInfo())
        # Sort the players
        self.players.sort(key=lambda player: player.position, reverse=True)
        if self.GUI_player:
            self.GUI_player.output_queue.put_nowait("Game over. Result:")
            for player in self.players:
                self.GUI_player.output_queue.put_nowait(f"{player.name}: {player.position}")

            # the game is over, but we call `_choose_cards_to_play()` one last time
            # just to update the user interface.
            # This call won't return because there are no legal moves to play
            if self.players[0] is self.GUI_player:
                await self.GUI_player._choose_cards_to_play(self.players[1:])
            else:
                await self.GUI_player._choose_cards_to_play(self.players[:1])

    def print_result(self):
        print("GAME OVER! Result:")
        for player in self.players:
            print(player)
