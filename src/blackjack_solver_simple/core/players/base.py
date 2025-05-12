from __future__ import annotations
from abc import ABC
from typing import Protocol
# care for circular import
from blackjack_solver_simple.core.hand import Hand
from blackjack_solver_simple.core.state import UniversalBJState


class Policy(Protocol):
    def decide(self, state: UniversalBJState) -> str:
        ...


class Player(ABC):

    def __init__(self, policy: Policy) -> None:
        self.policy: Policy = policy
        self.hand = Hand([])

    def reset(self) -> None:
        """Reset player hand to an empty hand
        """
        self.hand = Hand([])  # empty hand, we'll draw later

    def decide(self, state: UniversalBJState) -> str:
        """Wrapper so env doesn't directly talk to the policy.
           For actual documentation on this look at policy.decide()

        Args:
            state (Tuple): current state

        Returns:
            str: "hit" or "stand"
        """
        return self.policy.decide(state)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.hand}"
