from __future__ import annotations
import random
from typing import Tuple

from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.state import BJState


class RandomPolicy(Policy):

    def decide(self, state: BJState) -> str:
        return random.choice(("hit", "stand"))


class TabularQPolicy:
    # TODO
    ...
