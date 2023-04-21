import asyncio

from players import *
from carddict import cardDict


class Card:
    def __init__(self, number, symbol):
        self.number = number
        self.symbol = symbol

    def __str__(self):
        return f"<{self.number} ({self.symbol})>"

    def __repr__(self):
        return self.__str__()


class Game:
    def __init__(self, *players):
        assert len(players) >= 2, "The number of players must be at least 2."

        self.verbose = False
        self.players = [player if isinstance(player, Player) else Human(player) for player in players]

        self.deck = [Card(number, symbol) for number, primes in cardDict.items() for symbol in primes]
        random.shuffle(self.deck)

        self.number_of_setbacks = 0
        self.number_of_turns = 0

    def _draw_for_player(self, player):
        if self.deck:
            player.receive_card(self.deck.pop())

    def set_verbose(self, verbose):
        self.verbose = verbose

    def run(self):
        """
        Play the game until one player wins or all players pass. Leaves `self.players` sorted by winner.
        :return: None
        """
        asyncio.run(self.gameplay())

    async def gameplay(self):
        for player in self.players:
            player.reset()
        # deal one card to each player
        for player in self.players:
            self._draw_for_player(player)
        self.number_of_passes = 0
        continue_move = False
        all_cards_played = []

        while self.number_of_passes < len(self.players):
            if not continue_move:
                all_cards_played = []
                self.number_of_turns += 1
            player = self.players[0]
            opponents = self.players[1:]
            if self.verbose:
                print(f"{player} to play.")
            cards, revealed = await player.play_cards(opponents)
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
                    assert can_setback, "Can't reveal cards unless setting back an opponent." # RULE
                    for opponent in opponents:
                        if opponent.symbols_match(symbols):
                            opponent.move(-delta)
                            player.move(delta) # RULE: move forward for each opponent that is set back
                            self.number_of_setbacks += 1
                    cards_played = cards
                    continue_move = True
                else:
                    assert len(set(numbers)) == 1, "Can't play different numbers unless setting back someone." # RULE
                    player.move(delta)
                    cards_played = [card.number for card in cards]
                    continue_move = False
                all_cards_played += cards_played
                if self.verbose:
                    print(f"{player.name} plays {' '.join(str(card) for card in cards_played)}")

                if player.position == 100:
                    break

            # RULE: If a player reveals cards, they can continue their move.
            # If they don't, they draw new cards and it's the next player's turn.
            if not continue_move:
                for opponent in opponents:
                    opponent.receive_information(player, all_cards_played)

                for _ in range(len(all_cards_played) + 1): # RULE: draw one more card than played
                    self._draw_for_player(player)

                self.players = opponents + [player] # rotate players

        # game over. Sort the players
        self.players.sort(key=lambda player: player.position, reverse=True)

    def print_result(self):
        print("GAME OVER! Result:")
        for player in self.players:
            print(player)
