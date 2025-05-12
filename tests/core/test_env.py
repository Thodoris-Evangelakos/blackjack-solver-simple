import random
import pytest  # type: ignore
from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.core.state import UniversalBJState
from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.card import Card, Rank, Suit
from blackjack_solver_simple.core.hand import Hand


# 1. Stub policy that always stands
class StubPolicy(Policy):
    def decide(self, state):
        return "stand"


# 2. Test _add_visible and _bin_count
def test_add_visible_and_bin_count():
    env = BlackJackEnv(player_policy=StubPolicy())
    # fake card with hilo_weight = 1
    fake_card = Card(Rank.TWO, Suit.SPADES)
    assert env.visible_count == 0
    env._add_visible(fake_card)
    assert env.visible_count == 1
    # test thresholds
    env.visible_count = 6
    assert env._bin_count() == +1
    env.visible_count = -6
    assert env._bin_count() == -1
    env.visible_count = 5
    assert env._bin_count() == 0
    env.visible_count = -5
    assert env._bin_count() == 0


# 3. Test _reshuffle_if_needed
def test_reshuffle_if_needed(monkeypatch):
    env = BlackJackEnv(player_policy=StubPolicy())

    class DummyDeck:
        def cards_left(self): return 5
    dummy = DummyDeck()
    env.deck = dummy  # type: ignore
    env.visible_count = 42
    env._reshuffle_if_needed()
    # deck should be replaced by a real Deck
    assert not isinstance(env.deck, DummyDeck)
    # visible count reset
    assert env.visible_count == 0


# 4. Test _encode_state
def test_encode_state(monkeypatch):
    env = BlackJackEnv(player_policy=StubPolicy())
    # stub internals
    env._dealer_up_value = 7
    env.visible_count = 3
    # stub player's hand attributes
    monkeypatch.setattr(env.player.hand, "_hand_value", 15)
    monkeypatch.setattr(env.player.hand, "_is_soft", True)
    state = env._encode_state()
    assert isinstance(state, UniversalBJState)
    assert state.player_total == 15
    assert state.dealer_up == 7
    assert state.player_soft is True
    assert state.count_bin == 0  # visible_count=3 -> bin=0
    assert state.dealer_total is None
    assert state.dealer_soft is None


# 5. Test reset basic behavior
def test_reset_basic():
    rng = random.Random(0)
    env = BlackJackEnv(player_policy=StubPolicy(), rng=rng)
    state = env.reset()
    assert isinstance(state, UniversalBJState)
    assert env._done is False
    assert state.count_bin in (-1, 0, 1)


# 6. Test invalid action and done-state errors
def test_step_invalid_and_done_errors():
    env = BlackJackEnv(player_policy=StubPolicy())
    env.reset()
    with pytest.raises(ValueError):
        env.step("noop")
    env._done = True
    with pytest.raises(RuntimeError):
        env.step("hit")


# 7. Test hit -> bust(-1) and blackjack(+1)
def test_step_hit_bust():
    env = BlackJackEnv(player_policy=StubPolicy(), rng=random.Random(0))

    # force the player's hand to a "hard 20"
    env.player.hand = Hand([
        Card(Rank.TEN, Suit.HEARTS),
        Card(Rank.TEN, Suit.CLUBS),
    ])

    # push a King (value 10) on top of the deck → total becomes 30 → bust
    env.deck._cards.insert(0, Card(Rank.KING, Suit.SPADES))

    # force a _dealer_up_value so state encoding doesn't fail
    env._dealer_up_value = 7
    state, reward, done, info = env.step("hit")
    assert reward == -1 and done


def test_step_hit_blackjack():
    env = BlackJackEnv(player_policy=StubPolicy(), rng=random.Random(0))

    # force the player's hand to total 10
    env.player.hand = Hand([
        Card(Rank.TEN, Suit.HEARTS)
    ])

    # push an Ace (11) on top → total becomes 21 → blackjack
    env.deck._cards.insert(0, Card(Rank.ACE, Suit.CLUBS))

    # force a _dealer_up_value so state encoding doesn't fail
    env._dealer_up_value = 7
    state, reward, done, info = env.step("hit")
    assert reward == +1 and done


# 8. Test stand invokes dealer turn and resolves reward
def test_step_stand_invokes_dealer_and_resolve(monkeypatch):
    env = BlackJackEnv(player_policy=StubPolicy())
    env.reset()
    # stub dealer turn and resolve
    called = {}
    monkeypatch.setattr(env, "_dealer_turn", lambda: called.setdefault("turned", True))
    monkeypatch.setattr(env, "_resolve_reward", lambda: 42)
    state, reward, done, info = env.step("stand")
    assert called.get("turned", False) is True
    assert reward == 42 and done
