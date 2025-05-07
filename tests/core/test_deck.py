import random
import pytest
from blackjack_solver_simple.core.card import Card, Rank, Suit
from blackjack_solver_simple.core.deck import Deck


def test_deck_contains_52_unique_cards():
    deck = Deck(random.Random(0))
    assert deck.cards_left() == 52
    all_drawn = deck.draw(52)
    assert len(all_drawn) == 52
    assert len(set(all_drawn)) == 52          # hashability matters
    assert deck.cards_left() == 0


def test_draw_raises_exception_when_empty():
    deck = Deck(random.Random(0))
    deck.draw(52)  # Draw all cards
    with pytest.raises(ValueError, match="Not enough cards left in the deck."):
        deck.draw(1)


def test_shuffle_changes_order():
    rng1 = random.Random(123)
    rng2 = random.Random(123)
    d1 = Deck(rng1)
    d2 = Deck(rng2)
    # same seed ⇒ identical order
    assert d1.draw(52) == d2.draw(52)
    # now reshuffle one deck with *new* seed
    # resetting d2 because we would run out of cards
    d2 = Deck(rng1)
    d1 = Deck(random.Random(999))
    assert d1.draw(52) != d2.draw(52)

