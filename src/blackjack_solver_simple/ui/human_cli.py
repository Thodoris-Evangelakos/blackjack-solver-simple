# not sure if this should be in the ui folder or not but w/e

from typing import Tuple
from blackjack_solver_simple.core.players.base import Policy


class HumanCliPolicy(Policy):
    
    def decide(self, state: Tuple) -> str:
        """Player chooses whether to hit or stand based on CLI input.

        Args:
            state (Tuple): current state, not used here obviously

        Returns:
            str: "hit" or "stand"
        """
        while True:
            user = input("Hit or Stand? (h/s): ").strip().lower()
            if user in ("h", "hit"):
                return "hit"
            elif user in ("s", "stand"):
                return "stand"
            else:
                print("Invalid input. Please enter 'h' for hit or 's' for stand.")