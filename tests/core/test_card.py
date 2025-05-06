import pytest
from blackjack_solver_simple.core.card import Card, Rank, Suit


def test_ace_values():
    ace = Card(Rank.ACE, Suit.SPADES)
    assert ace.blackjack_value(True) == 11
    assert ace.blackjack_value(False) == 1


def test_hilo_weights():
    assert Card(Rank.FIVE, Suit.HEARTS).hilo_weight() == 1
    assert Card(Rank.TEN,  Suit.CLUBS).hilo_weight() == -1


def test_equality_and_hash():
    c1 = Card(Rank.SEVEN, Suit.DIAMONDS)
    c2 = Card(Rank.SEVEN, Suit.DIAMONDS)
    assert c1 == c2 and hash(c1) == hash(c2)
