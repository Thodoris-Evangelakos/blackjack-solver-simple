from blackjack_solver_simple.core.players.base import Player, Policy


class Agent(Player):
    def __init__(self, policy: Policy) -> None:
        super().__init__(policy)
