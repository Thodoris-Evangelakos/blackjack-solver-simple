from typing import NamedTuple


class BJState(NamedTuple):
    """Named tuple containing the current state of the game, passed to agents/dealer to decide policy

    Members:
        player_total (int): Player's total score (calculated from hand)
        dealer_up (int): Dealer's visible card value
        player_soft (bool): True if player hand is soft (at least 1 ace counts as 11)
        count_bin (int): Current count bin (for card counting)

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
