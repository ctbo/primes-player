# Play the primes game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

from players import *


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


class Game:
    def __init__(self, *players):
        assert len(players) >= 2, "The number of players must be at least 2."

        self.verbose = False
        self.players = [player if isinstance(player, Player) else Human(player) for player in players]

        self.deck = [Card(number, symbol) for number, primes in enumerate(cardPrimes) for symbol in primes]
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
            cards, revealed = player.play_cards(opponents)
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


class Tournament:
    def __init__(self, *players):
        assert len(players) >= 2, "The number of players must be at least 2."
        self.verbose = False
        self.players = [player if isinstance(player, Player) else Human(player) for player in players]
        self.scores = {id(player): 0 for player in self.players}
        self.games_played = 0
        self.number_of_turns = 0
        self.number_of_setbacks = 0
        self.number_used_all_cards = 0
        self.number_of_cards_left = 0
        self.winning_score = 0

    def set_verbose(self, verbose):
        self.verbose = verbose

    def score(self, finished_game):
        """
        Score a game. Given the final position of a games, update self.scores and other stats
        :param finished_game: a finished game
        :return: None
        """
        self.games_played += 1
        best_position = finished_game.players[0].position
        self.winning_score += best_position
        i = 1
        while i < len(finished_game.players) and finished_game.players[i].position == best_position:
            i += 1
        for j in range(i):
            self.scores[id(finished_game.players[j])] += 1 / i

    def run(self, rounds):
        for i in range(rounds):
            g = Game(*self.players)
            g.set_verbose(self.verbose)
            g.run()
            if self.verbose:
                g.print_result()
            self.score(g)
            self.number_of_turns += g.number_of_turns
            self.number_of_setbacks += g.number_of_setbacks
            self.number_of_cards_left += len(g.deck)
            self.number_used_all_cards += len(g.deck) == 0

    def print_results(self):
        if self.games_played:
            print(f"Tournament results after {self.games_played} games:")
            total_scores = sum(self.scores.values())
            for player in self.players:
                score = self.scores[id(player)]
                print(f"{player.name}: {score:.2f} ({score/total_scores*100:.1f}%)")
            print(f"""Averages per game: {self.number_of_turns/self.games_played:.1f} moves, {
                self.number_of_setbacks/self.games_played:.1f} setbacks, winning score {
                self.winning_score/self.games_played:.1f}, {
                self.number_of_cards_left/self.games_played:.1f} cards in deck""")
            print(f"{self.number_used_all_cards/self.games_played*100:.1f}% of games used all cards.")
        else:
            print("No games have been played yet.")

if __name__ == '__main__':
    # g = Game("Harald", Forrest())
    # g.run()
    # g.print_result()
    # exit()

    t = Tournament(GreedyTortoise(), GreedyTortoise(), Forrest(), Forrest())
    # t.set_verbose(True)
    while True:
        t.run(1000)
        t.print_results()
