from blackjack_solver_simple.core.card import Card, Rank, Suit


class Hand:
    def __init__(self, cards: list[Card]):
        self.cards = cards  # hand is always initialized with 2 cards so no prob here
        self.hand_value = 0
        self.is_soft = False  # True if it has at least 1 ace = 11

    def add_card(self, cards: list[Card]) -> None:
        """Adds a list of cards to the hand and updates the hand value.
           Not sure when we'd add more than 1 card, but draw returns a list so
           this is a good way to handle the list logic internally.
           UPDATING THE VALUE/SOFT BOOL IS HANDLED HERE, DON'T CALL IT IN ENV

        Args:
            cards (list[Card]): the card(s) we're adding

        Returns:
            None: None
        """
        self.cards.extend(cards)  # deck's draw method returns a list
        self.update_hand_value()
        return None

    def update_hand_value(self) -> None:
        """Calculates the highest possible value of the hand and updates the hand_value attribute.
           Also updates the is_soft boolean. Converts aces from high to low until it is under 21 or runs out of aces.
           The whole idea behind this is avoiding the need to calculate the 2^(#aces) possible values of the hand.

        Returns:
            None: Doesn't return anything, use a get method to get the value after updating
        """
        number_of_high_aces = sum(card.rank is Rank.ACE for card in self.cards)
        value = sum(card.blackjack_value(True) for card in self.cards)  # treat every ace as 11 initialy
        while value > 21 and number_of_high_aces > 0:
            value -= 10
            number_of_high_aces -= 1
        self.hand_value = value
        self.is_soft = number_of_high_aces > 0
        return None

    # ~~~~~~~~~~ helper methods ~~~~~~~~~~ #

    def is_21(self) -> bool:
        """Checks if the hand value is 21.

        Returns:
            bool: True if the hand value is 21, False otherwise.
        """
        return self.hand_value == 21

    def is_blackjack(self) -> bool:
        """Checks if the hand is a (natural) blackjack (an ace and a 10-eq card).

        Returns:
            bool: True if the hand is a blackjack, False otherwise.
        """
        return len(self.cards) == 2 and self.is_21()

    def is_bust(self) -> bool:
        """Checks if the hand is bust (over 21).

        Returns:
            bool: True if the hand is bust, False otherwise.
        """

        if self.is_soft and self.hand_value > 21:
            raise ValueError("Soft hand cannot be bust.")
        return self.hand_value > 21

    # ~~~~~~~~~~ dunder methods ~~~~~~~~~~ #

    def __str__(self) -> str:
        return f"{self.cards} (value: {self.hand_value}, soft: {self.is_soft})"


if __name__ == "__main__":
    # testing primarily aesthetics of printing
    # hmm, cards are being printed as <object at 0xdeadbeef> instead of the __str__ method
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    print(hand)  # Output: [Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.TEN, suit=Suit.HEARTS)] (value: 21, soft: True)

    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand.add_card([card3])

    print(hand)  # Output: [Card(rank=Rank.ACE, suit=Suit.SPADES), Card(rank=Rank.TEN, suit=Suit.HEARTS), Card(rank=Rank.FIVE, suit=Suit.DIAMONDS)] (value: 16, soft: False)
