from enum import IntEnum, Enum


class Suit(Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"


class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


_HI_LO = {
    Rank.TWO: 1, Rank.THREE: 1, Rank.FOUR: 1, Rank.FIVE: 1, Rank.SIX: 1,
    Rank.SEVEN: 0, Rank.EIGHT: 0, Rank.NINE: 0,
    Rank.TEN: -1, Rank.JACK: -1, Rank.QUEEN: -1, Rank.KING: -1, Rank.ACE: -1
}


class Card:
    __slots__ = ("rank", "suit")  # slotting performance boost?

    def __init__(self, rank: Rank, suit: Suit) -> None:
        self.rank = rank
        self.suit = suit

    # ~~~~~~~~~~ helper methods ~~~~~~~~~~ #

    def blackjack_value(self, ace_high: bool = True) -> int:
        """ Returns card value.
                Special case for ace, depending on what the player chooses

        Args:
            ace_high (bool, optional): Whether the ace counts as 11 or 1.
                Default value is 11.

        Returns:
            int: card value
        """
        if self.rank is Rank.ACE:
            return 11 if ace_high else 1
        return min(int(self.rank), 10)

    def hilo_weights(self) -> int:
        return _HI_LO[self.rank]

    # ~~~~~~~~~~ dunder methods ~~~~~~~~~~ #

    def __reppr__(self) -> str:
        return f"Card(rank={self.rank}, suit={self.suit})"

    def __str__(self) -> str:
        symbols = {Rank.JACK: "J", Rank.QUEEN: "Q", Rank.KING: "K", Rank.ACE: "A"}
        rank_str = symbols.get(self.rank, str(self.blackjack_value()))
        return f"{rank_str}{self.suit.value}"

    def __eq__(self, other) -> bool:
        return isinstance(other, Card) and (self.rank, self.suit) == (other.rank, other.suit)

    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
