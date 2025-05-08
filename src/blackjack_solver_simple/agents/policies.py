from __future__ import annotations
import random
from typing import Tuple

from blackjack_solver_simple.core.players.base import Policy


class RandomPolicy(Policy):

    def decide(self, state: Tuple) -> str:
        return random.choice(("hit", "stand"))


class TabularQPolicy:
    # TODO
    ...
