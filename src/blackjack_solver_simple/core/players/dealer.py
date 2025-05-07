from __future__ import annotations
from typing import Callable

from blackjack_solver_simple.core.players.base import Player, Policy
from blackjack_solver_simple.core.hand import Hand
from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.card import Card, Rank


class _DealerPolicy:
    def decide(self, state):
        # unused, the dealer plays immideately
        ...


class Dealer(Player):

    def __init__(self) -> None:
        super().__init__(_DealerPolicy())
        self._hole_card: Card | None = None  # set/revealed by env

    def play(self, deck: Deck, add_visible_count: Callable[[Card], None]) -> None:
        pass