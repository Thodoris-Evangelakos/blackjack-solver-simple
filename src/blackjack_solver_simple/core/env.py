from blackjack_solver_simple.core.deck import Deck


class BlackJackEnv:

    def __init__(self, rng=None):
        self._rng = rng
        self._deck = Deck(rng)
        self.running_count_visible = 0

    def reset(self):
        if self._deck.cards_left() < 10:
            self._deck = Deck(self._rng)
            self.running_count_visible = 0
