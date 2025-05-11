import random
from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.card import Card, Rank, Suit
from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.core.players.base import Policy

def test_reset_sets_initial_state_and_visible_count():

    class DummyDeck(Deck):
        def __init__(self, cards):
            self.cards = cards.copy()
        def cards_left(self):
            return len(self.cards)
        def draw(self, n):
            drawn, self.cards = self.cards[:n], self.cards[n:]
            return drawn

    class StandPolicy(Policy):
        def decide(self, state):
            return "stand"

    # Prepare a fixed sequence: player 2+3, dealer up 5, hole 6
    fixed_cards = [Card(Rank.TWO, Suit.HEARTS), Card(Rank.THREE, Suit.HEARTS),
                   Card(Rank.FIVE, Suit.HEARTS), Card(Rank.SIX, Suit.HEARTS)]
    env = BlackJackEnv(player_policy=StandPolicy())
    env.deck = DummyDeck(fixed_cards)
    env.dealer.policy = StandPolicy()

    state = env.reset()
    assert state.player_total == 5
    assert state.dealer_up == 5
    # hilo weights for 2,3,5 are +1 each
    assert env.visible_count == 3

    # stand immediately -> dealer reveals 6, stands -> dealer 11 vs player 5 -> lose
    new_state, reward, done, info = env.step("stand")
    assert done is True
    assert reward == -1
    assert info == {}

def test_invalid_action_raises_ValueError():

    class HitPolicy(Policy):
        def decide(self, state):
            return "hit"

    env = BlackJackEnv(player_policy=HitPolicy())
    env.reset()
    with pytest.raises(ValueError):
        env.step("foo")

def test_step_after_done_raises_RuntimeError():

    class StandPolicy(Policy):
        def decide(self, state):
            return "stand"

    env = BlackJackEnv(player_policy=StandPolicy())
    env.reset()
    # simulate end of round
    env._done = True
    with pytest.raises(RuntimeError):
        env.step("hit")