import pytest
from blackjack_solver_simple.core.card import Card, Rank, Suit
from blackjack_solver_simple.core.hand import Hand


def test_hand_initialization():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    assert hand.cards == [card1, card2]
    assert hand.hand_value == 0  # Value is updated only after calling update_hand_value
    assert hand.is_soft is False


def test_add_card():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand = Hand([card1, card2])

    hand.add_card([card3])
    assert len(hand.cards) == 3
    assert card3 in hand.cards


def test_update_hand_value():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    hand.update_hand_value()
    assert hand.hand_value == 21
    assert hand.is_soft is True

    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand.add_card([card3])
    assert hand.hand_value == 16
    assert hand.is_soft is False


def test_is_21():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    hand.update_hand_value()
    assert hand.is_21() is True

    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand.add_card([card3])
    assert hand.is_21() is False


def test_is_blackjack():
    card1 = Card(Rank.ACE, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    hand = Hand([card1, card2])

    hand.update_hand_value()
    assert hand.is_blackjack() is True

    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand.add_card([card3])
    assert hand.is_blackjack() is False


def test_is_bust():
    card1 = Card(Rank.TEN, Suit.SPADES)
    card2 = Card(Rank.TEN, Suit.HEARTS)
    card3 = Card(Rank.FIVE, Suit.DIAMONDS)
    hand = Hand([card1, card2])

    hand.add_card([card3])
    assert hand.is_bust() is True

    card4 = Card(Rank.ACE, Suit.CLUBS)
    hand = Hand([card1, card4])
    hand.update_hand_value()
    assert hand.is_bust() is False

    with pytest.raises(ValueError):
        hand.is_soft = True
        hand.hand_value = 22
        hand.is_bust()
