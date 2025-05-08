from __future__ import annotations
import random
from typing import Tuple

from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.state import BJState

class DealerPolicy(Policy):
    def decide(self, state: BJState) -> str:
        total = state.dealer_total
        soft = state.dealer_soft  # noqa F401
        assert total is not None, "Dealer's total should be revealed/filled in env"

        if total <= 16:
            return "hit"
        else:
            return "stand"


class RandomPolicy(Policy):

    def decide(self, state: BJState) -> str:
        return random.choice(("hit", "stand"))


class TabularQPolicy:
    # TODO
    ...
