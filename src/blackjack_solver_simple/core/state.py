from abc import ABC


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


class UniversalBJState(State):
    def __init__(self, player_total: int, dealer_up: int, player_soft: bool, count_bin: int,
                 dealer_total: int | None = None, dealer_soft: bool | None = None):
        super().__init__(player_total, dealer_up, player_soft)
        self.count_bin = count_bin
        self.dealer_total = dealer_total
        self.dealer_soft = dealer_soft

    def tuple_full(self) -> tuple[int, int, bool, int, int | None, bool | None]:
        """Returns the full state as a tuple
        """
        return (self.player_total, self.dealer_up, self.player_soft,
                self.count_bin, self.dealer_total, self.dealer_soft)

    def tuple_Q(self) -> tuple[int, int, bool]:
        """Returns the Q state as a tuple
        """
        return (self.player_total, self.dealer_up, self.player_soft)

    def tuple_Q_counting(self) -> tuple[int, int, bool, int]:
        """Returns the Q state with counting as a tuple
        """
        return (self.player_total, self.dealer_up, self.player_soft, self.count_bin)

    def hash_full(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft,
                     self.count_bin, self.dealer_total, self.dealer_soft))

    def hash_Q(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft))

    def hash_Q_counting(self) -> int:
        return hash((self.player_total, self.dealer_up, self.player_soft, self.count_bin))
