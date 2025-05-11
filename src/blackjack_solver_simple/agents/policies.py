from __future__ import annotations
import random
from typing import Tuple
from collections import defaultdict
import numpy as np
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



class TabularQPolicy(Policy):

    def __init__(self, env:Env,learning_rate: float,initial_epsilon: float,gamma: float):
        self.env = env
        self.q_values = defaultdict(lambda: np.zeros(env.action_space.n))

        self.alpha = learning_rate
        self.gamma = gamma

        self.epsilon = initial_epsilon
        self.training_error_qlearning = []
        self.training_error_sarsa = []


    def decide(self, state: BJState):
        if np.random.random() < self.epsilon:
            return self.env.action_space.sample()
        else:
            return int(np.argmax(self.q_values[BJState]))
            
    def _update(self, state: BJState, action: int, reward: float,terminated:int,next_state: tuple[int, int, int]) -> None:
        if terminated:
            future_q_value = 0.0
        else:
            future_q_value = np.max(self.q_values[next_state])

        temporal_difference = (reward + self.gamma * future_q_value - self.q_values[state][action] )

        self.q_values[state][action] = (self.q_values[state][action] + self.alpha * temporal_difference)

        #represents the difference between the current Q‑value estimate and the “target” value computed from the reward and the estimated future Q‑values
        self.training_error_qlearning.append(temporal_difference)
    
