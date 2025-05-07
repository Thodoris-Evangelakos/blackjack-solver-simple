import pytest
from unittest.mock import MagicMock
from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.core.players.base import Policy


def test_blackjack_env_initialization():
    mock_policy = MagicMock(spec=Policy)
    env = BlackJackEnv(player_policy=mock_policy)

    assert env._rng is None
    assert env.player.policy == mock_policy
    assert isinstance(env.dealer, MagicMock) is False  # Dealer is not mocked here
    assert env._deck is not None


def test_blackjack_env_reset_with_low_cards():
    mock_policy = MagicMock(spec=Policy)
    mock_deck = MagicMock()
    mock_deck.cards_left.return_value = 5  # Simulate low cards in the deck

    env = BlackJackEnv(player_policy=mock_policy)
    env._deck = mock_deck  # Replace the deck with the mock

    env.reset()

    assert env._deck.cards_left.call_count == 1