from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.players.dealer import Dealer
from blackjack_solver_simple.core.players.agent import Agent
from blackjack_solver_simple.core.players.base import Policy


class BlackJackEnv:

    def __init__(self, player_policy: Policy, *, rng=None):
        self._rng = rng
        self._deck = Deck(rng)
        self.player = Agent(player_policy)
        self.dealer = Dealer()

    def reset(self):
        if self._deck.cards_left() < 10:
            self._deck = Deck(self._rng)
            self.running_count_visible = 0
