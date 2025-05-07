from __future__ import annotations
from typing import Callable

from blackjack_solver_simple.core.players.base import Player, Policy
from blackjack_solver_simple.core.hand import Hand
from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.card import Card, Rank


class _DealerPolicy