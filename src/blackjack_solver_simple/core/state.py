from typing import NamedTuple
from abc import ABC

class BJState(NamedTuple):
    """Named tuple containing the current state of the game, passed to agents/dealer to decide policy

    Members:
        player_total (int): Player's total score (calculated from hand)
        dealer_up (int): Dealer's visible card value
        player_soft (bool): True if player hand is soft (at least 1 ace counts as 11)
        count_bin (int): Current count bin. +1 if running count > +5, -1 if running count < -5, 0 otherwise

        dealer_total (int | None): Dealer's total score (calculated from hand), None if not yet revealed
        dealer_soft (bool | None): True if dealer hand is soft, None if not yet revealed
    """

    # ~~~~~~~~~~ player info ~~~~~~~~~~ #
    player_total: int
    dealer_up: int
    player_soft: bool
    count_bin: int

    # ~~~~~~~~~~ dealer info ~~~~~~~~~~ #
    dealer_total: int | None
    dealer_soft: bool | None


class BJStateQ(NamedTuple):
    """Same as BJState, but without dealer or card counting info
    """

    # ~~~~~~~~~~ player info ~~~~~~~~~~ #
    player_total: int
    dealer_up: int
    player_soft: bool


class State(ABC):
    def __init__(self, player_total: int, dealer_up: int, player_soft: bool):
        self.player_total = player_total
        self.dealer_up = dealer_up
        self.player_soft = player_soft

    def __hash__(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft))

    def as_key(self) -> str:
        """Returns a string representation of the state, suitable for use as a dictionary key
        """
        return f"{self.player_total}_{self.dealer_up}_{int(self.player_soft)}"


class BJState(State):
    def __init__(self, player_total: int, dealer_up: int, player_soft: bool, count_bin: int, dealer_total: int | None = None, dealer_soft: bool | None = None):
        super().__init__(player_total, dealer_up, player_soft)
        self.count_bin = count_bin
        self.dealer_total = dealer_total
        self.dealer_soft = dealer_soft

    def __hash__(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft, self.count_bin, self.dealer_total, self.dealer_soft))

    def as_key(self) -> str:
        """Returns a string representation of the state, suitable for use as a dictionary key
        """
        return f"{self.player_total}_{self.dealer_up}_{int(self.player_soft)}_{self.count_bin}_{self.dealer_total}_{int(self.dealer_soft)}"


class BJStateQ(State):
    def __init__(self, player_total: int, dealer_up: int, player_soft: bool):
        super().__init__(player_total, dealer_up, player_soft)

    def __hash__(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft))

    def as_key(self) -> str:
        """Returns a string representation of the state, suitable for use as a dictionary key
        """
        return f"{self.player_total}_{self.dealer_up}_{int(self.player_soft)}"


class BJStateQCounting(State):
    def __init__(self, player_total: int, dealer_up: int, player_soft: bool, count_bin: int):
        super().__init__(player_total, dealer_up, player_soft)
        self.count_bin = count_bin

    def __hash__(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft, self.count_bin))

    def as_key(self) -> str:
        """Returns a string representation of the state, suitable for use as a dictionary key
        """
        return f"{self.player_total}_{self.dealer_up}_{int(self.player_soft)}_{self.count_bin}"
