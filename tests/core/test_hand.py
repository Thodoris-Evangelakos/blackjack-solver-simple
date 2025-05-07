import pytest
from blackjack_solver_simple.core.card import Card, Rank, Suit
from blackjack_solver_simple.core.hand import Hand


def test_hand_initialization():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    assert hand.hand_value == 21
    assert hand.is_soft is True
    assert hand.is_blackjack() is True
    assert hand.is_21() is True
    assert hand.is_bust() is False


def test_add_card():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand = Hand([card1, card2])

    hand.add_cards([card3])

    assert hand.hand_value == 16
    assert hand.is_soft is False
    assert hand.is_blackjack() is False
    assert hand.is_21() is False
    assert hand.is_bust() is False


def test_bust_hand():
    card1 = Card(Rank.TEN, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    card3 = Card(Rank.TWO, Suit.DIAMONDS)
    hand = Hand([card1, card2])

    hand.add_cards([card3])

    assert hand.hand_value == 22
    assert hand.is_soft is False
    assert hand.is_blackjack() is False
    assert hand.is_21() is False
    assert hand.is_bust() is True


def test_soft_hand():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.SIX, Suit.HEARTS)
    hand = Hand([card1, card2])

    assert hand.hand_value == 17
    assert hand.is_soft is True
    assert hand.is_blackjack() is False
    assert hand.is_21() is False
    assert hand.is_bust() is False


def test_hard_hand_after_ace_conversion():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.SIX, Suit.HEARTS)
    card3 = Card(Rank.SIX, Suit.DIAMONDS)
    hand = Hand([card1, card2])

    hand.add_cards([card3])

    assert hand.hand_value == 13
    assert hand.is_soft is False
    assert hand.is_blackjack() is False
    assert hand.is_21() is False
    assert hand.is_bust() is False


def test_str_representation():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    assert str(hand) == "[A♠ 10♥] (value: 21, soft: True)"
