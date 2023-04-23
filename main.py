# Play the primes game
# Game design: Grant Sinclair
# Code: Harald Bögeholz

from game import *


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
    g = Game(Forrest(), GUI())
    g.run()
    g.print_result()
    exit()

    t = Tournament(RandomNoPassBot(), RandomNoPassBot())
    # t.set_verbose(True)
    while True:
        t.run(1000)
        t.print_results()
