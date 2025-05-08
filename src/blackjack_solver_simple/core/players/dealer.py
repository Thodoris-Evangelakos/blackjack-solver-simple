from __future__ import annotations
from typing import Callable

from blackjack_solver_simple.core.players.base import Player, Policy
from blackjack_solver_simple.core.hand import Hand
from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.card import Card, Rank
from blackjack_solver_simple.core.state import BJState


class _DealerPolicy:
    def decide(self, state: BJState) -> str:
        total = state.dealer_total
        soft = state.dealer_soft  # noqa F401
        assert total is not None, "Dealer's total should be revealed/filled in env"

        if total <= 16:
            return "hit"
        else:
            return "stand"


class Dealer(Player):

    def __init__(self) -> None:
        super().__init__(_DealerPolicy())
        self.hole_card: Card | None = None  # set/revealed by env

    def play(self, deck: Deck, add_visible_count: Callable[[Card], None]) -> None:
        # ENDED UP NOT USING THIS
        pass
