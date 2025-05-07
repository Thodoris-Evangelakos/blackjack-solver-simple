from blackjack_solver_simple.core.card import Card, Rank, Suit


class Hand:
    def __init__(self, cards: list[Card]):
        """Implements the Hand class. Contains useful information like value and soft_hand.
           value: highest possible value of the hand
           soft_hand: boolean indicating whether the hand is soft (contains an ace counted as 11)

        Args:
            cards (list[Card]): Cards the hand is initialized with. Probably 2 cards.
        """
        self._cards = cards
        self._hand_value = 0
        self._is_soft = False
        self._recompute()

    @property
    def cards(self) -> tuple[Card, ...]:
        """Returns the cards in the hand. Doing this so only an immutable tuple is returned
           and the user can't modify the list of cards directly without going through the add_card method.

        Returns:
            tuple[Card, ...]: The cards in the hand.
        """
        return tuple(self._cards)

    @property
    def hand_value(self) -> int:
        return self._hand_value

    @property
    def is_soft(self) -> bool:
        return self._is_soft

    def add_cards(self, cards: list[Card]) -> None:
        """Adds a list of cards to the hand and updates the hand value.
           Not sure when we'd add more than 1 card, but draw returns a list so
           this is a good way to handle the list logic internally.
           UPDATING THE VALUE/SOFT BOOL IS HANDLED HERE, DON'T CALL IT IN ENV

        Args:
            cards (list[Card]): the card(s) we're adding
        """
        self._cards.extend(cards)  # deck's draw method returns a list
        self._recompute()

    def _recompute(self) -> None:
        """Calculates the highest possible value of the hand and updates the hand_value attribute.
           Also updates the is_soft boolean. Converts aces from high to low until it is under 21 or runs out of aces.
           The whole idea behind this is avoiding the need to calculate the 2^(#aces) possible values of the hand.


        Returns:
            None: Doesn't return anything, use a get method to get the value after updating
        """
        number_of_high_aces = sum(card.rank == Rank.ACE for card in self._cards)
        value = sum(card.blackjack_value(True) for card in self._cards)  # treat every ace as 11 initialy
        while value > 21 and number_of_high_aces > 0:
            value -= 10
            number_of_high_aces -= 1
        self._hand_value = value
        self._is_soft = number_of_high_aces > 0

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
        return self.hand_value > 21

    # ~~~~~~~~~~ dunder methods ~~~~~~~~~~ #

    def __str__(self) -> str:
        return f"[{' '.join(str(c) for c in self.cards)}] (value: {self.hand_value}, soft: {self.is_soft})"

    def __itter__(self):
        """Allows iteration over the cards in the hand."""
        return iter(self.cards)


if __name__ == "__main__":
    # testing primarily aesthetics of printing
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    print(hand)

    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand.add_cards([card3])

    print(hand)
