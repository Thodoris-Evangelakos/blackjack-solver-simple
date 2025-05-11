from __future__ import annotations
import random
from collections import defaultdict
import numpy as np
from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.state import BJState, BJStateQ


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


# can't pickle anything that cointains a lambda function
def create_q_vector() -> np.ndarray:
    """Create a Q vector with 2 actions (hit, stand) initialized to 0.0"""
    return np.zeros(2)


class TabularQPolicy(Policy):
    # this mf can't win a single round, addicted to busting
    def __init__(self, learning_rate: float, initial_epsilon: float, gamma: float):
        # env only helped with action space cardinality (always 2) and sampling
        self.q_values = defaultdict(create_q_vector)

        self.alpha = learning_rate
        self.gamma = gamma

        self.epsilon = initial_epsilon
        self.training_error_qlearning = []
        self.training_error_sarsa = []

    def _convert_action_to_str(self, action: int) -> str:
        if action == 0:
            return "hit"
        elif action == 1:
            return "stand"
        else:
            raise ValueError(f"Invalid action: {action}")

    def _convert_action_to_int(self, action: str) -> int:
        if action == "hit":
            return 0
        elif action == "stand":
            return 1
        else:
            raise ValueError(f"Invalid action: {action}")

    # XXX:FIXME This is a very ugly hack, I should find a way to make BJStates hashable somehow
    def decide(self, state: str) -> str:
        # convert state to str for hashing
        if np.random.random() < self.epsilon:
            return random.choice(("hit", "stand"))
        else:
            return self._convert_action_to_str(int(np.argmax(self.q_values[state])))

    def _update(self, state: str, action: str, reward: float, terminated: int, next_state: str) -> None:
        # making state and next_state hashable (str instead of BJStateQ)
        _action = self._convert_action_to_int(action)
        if terminated:
            future_q_value = 0.0
        else:
            future_q_value = np.max(self.q_values[next_state])

        temporal_difference = (reward + self.gamma * future_q_value - self.q_values[state][_action])

        self.q_values[state][_action] = (self.q_values[state][_action] + self.alpha * temporal_difference)

        # represents the difference between the current Q‑value estimate and the “target” value computed from the reward and the estimated future Q‑values
        self.training_error_qlearning.append(temporal_difference)
