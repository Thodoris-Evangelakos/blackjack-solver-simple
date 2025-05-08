from __future__ import annotations
import random
from typing import Tuple, Any

from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.state import BJState
from blackjack_solver_simple.core.players.agent import Agent
from blackjack_solver_simple.core.players.dealer import Dealer
from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.card import Card


_WIN, _DRAW, _LOSE = +1, 0, -1  # constants for game results


class BlackJackEnv:

    def __init__(self, player_policy: Policy, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.deck: Deck = Deck(self.rng)
        self.visible_count: int = 0

        self.player = Agent(player_policy)
        self.dealer = Dealer()

        self._last_state: BJState | None = None
        self._done: bool = False

    # ~~~~~~~~~~ helper methods ~~~~~~~~~~ #
    def _add_visible(self, card: Card) -> None:
        self.visible_count += card.hilo_weight()

    def _bin_count(self) -> int | None:
        if self.phase == 1:  # type: ignore #FIXME
            return None
        if self.visible_count > 5:
            return +1
        elif self.visible_count < -5:
            return -1
        else:
            return 0

    # FIXME : COUNT_BIN MUST BE SET, RETURNING 0 PURELY FOR PHASE 0
    def _encode_state(self) -> BJState:
        state = BJState(
            player_total = self.player.hand.hand_value,
            dealer_up = self.dealer.hand.hand_value,
            player_soft = self.player.hand.is_soft,
            count_bin = 0,
            dealer_total = self.dealer
        )
        return state
