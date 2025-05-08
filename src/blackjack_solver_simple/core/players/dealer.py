from __future__ import annotations
from typing import Callable

from blackjack_solver_simple.core.players.base import Player, Policy
from blackjack_solver_simple.core.hand import Hand
from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.card import Card, Rank
from blackjack_solver_simple.core.state import BJState
from blackjack_solver_simple.agents.policies import DealerPolicy


class Dealer(Player):

    def __init__(self) -> None:
        super().__init__(DealerPolicy())
        self.hole_card: Card | None = None  # set/revealed by env

    def play(self, deck: Deck, add_visible_count: Callable[[Card], None]) -> None:
        # ENDED UP NOT USING THIS
        pass
