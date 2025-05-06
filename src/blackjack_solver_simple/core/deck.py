import random
from blackjack_solver_simple.core.card import Card, Rank, Suit


class Deck:
    def __init__(self, rng: random.Random | None = None) -> None:
        """Defines a pretty bare-bones deck of cards. Does shuffling and drawing

        Args:
            rng (random.Random | None, optional): randm.Random(seed) of choice. Defaults to random.Random().
        """
        # shoud I just let the user enter rng? might break my shuffling
        self._cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        self._rng = rng if rng else random.Random()
        self.shuffle()

    def shuffle(self) -> None:
        """Shuffles the deck in place using the provided random number generator.
        """
        self._rng.shuffle(self._cards)

    def draw(self, n: int = 1) -> list[Card]:
        """Draws the specified number of cards from the deck ('pops' them out).
           Designed to return a list of cards so that we can draw multiple cards at once.
        Args:
            n (int, optional): number of cards to be drawn. Defaults to 1.

        Raises:
            ValueError: asked to draw more cards than available in the deck.

        Returns:
            list[Card]: drawn cards.
        """
        
        # I should consider catching this and making a new deck instead
        # the deck is supposed to auto-renew once we're at less tha 10 cards anyway
        if n > self.cards_left():
            raise ValueError("Not enough cards left in the deck.")
        drawn_cards = self._cards[:n]
        self._cards = self._cards[n:]
        return drawn_cards

    def cards_left(self) -> int:
        """Ultra advanced method that calculates all of pi's digits
           compressed in a single line of code (wow!)

        Returns:
            int: number of cards left in the deck.
        """
        return len(self._cards)
