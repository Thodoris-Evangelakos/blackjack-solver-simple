from __future__ import annotations
import random
from typing import Tuple, Any

from blackjack_solver_simple.core.deck import Deck
from blackjack_solver_simple.core.state import BJState
from blackjack_solver_simple.core.players.agent import Agent
from blackjack_solver_simple.core.players.dealer import Dealer
from blackjack_solver_simple.core.players.base import Policy
from blackjack_solver_simple.core.card import Card


_WIN, _DRAW, _LOSE = +1, 0, -1  # constants for game results


class BlackJackEnv:

    def __init__(self, player_policy: Policy, *, rng: random.Random | None = None, counting_cards: bool = False) -> None:
        self.rng = rng or random.Random()
        self.deck: Deck = Deck(self.rng)

        self.visible_count: int = 0
        self._counting_cards = counting_cards

        self.player = Agent(player_policy)
        self.dealer = Dealer()

        self._dealer_up_value: int | None = None
        self._last_state: BJState | None = None
        self._done: bool = False

    # ~~~~~~~~~~ helper methods ~~~~~~~~~~ #
    def _add_visible(self, card: Card) -> None:
        """Updates the visible card "score", whenever a new card is revealed

        Args:
            card (Card): The card that was revealed
        """
        self.visible_count += card.hilo_weight()

    def _bin_count(self) -> int | None:
        """Crude indicator of whether the deck is "hot" or not

        Returns:
            int | None: None if we aren't counting cards
        """
        if self._counting_cards == 1:
            return None
        if self.visible_count > 5:
            return +1
        elif self.visible_count < -5:
            return -1
        else:
            return 0

    # FIXME : COUNT_BIN MUST BE SET, RETURNING 0 PURELY FOR PHASE 0
    def _encode_state(self) -> BJState:
        """Returns a BJState object containing the current state of the game.

        Returns:
            BJState: current state used to make decisions
        """
        state = BJState(
            player_total=self.player.hand.hand_value,
            dealer_up=self._dealer_up_value,
            player_soft=self.player.hand.is_soft,
            count_bin=self._bin_count(),
            dealer_total=None,
            dealer_soft=None,
        )
        return state

    def _reshuffle_if_needed(self) -> None:
        """Reshuffles the deck if there are less than 10 cards left.
        """
        if self.deck.cards_left() < 10:
            self.deck = Deck(self.rng)
            self.visible_count = 0

    # ~~~~~~~~~~ public API ~~~~~~~~~~ #

    def reset(self) -> BJState:
        """Start a fresh round, return initial observable state

        Returns:
            BJState: initial state
        """
        self._reshuffle_if_needed()

        self.player.reset()
        self.dealer.reset()
        self._done = False

        # ~~~~~~~~~~ initial deal ~~~~~~~~~~ #
        # 1. player draws 2 open cards
        cards = self.deck.draw(2)
        self.player.hand.add_cards(cards)
        for c in cards:
            self._add_visible(c)

        # 2. dealer draws 1 open card
        upcard = self.deck.draw(1)[0]
        self.dealer.hand.add_cards([upcard])
        self._add_visible(upcard)
        self._dealer_up_value = upcard.blackjack_value(True)

        # 3. dealer draws 1 hole card
        self.dealer.hole_card = self.deck.draw(1)[0]  # invisible for now

        self._last_state = self._encode_state()
        return self._last_state

    def step(self, action: str) -> Tuple[BJState, int, bool, dict[str, Any]]:
        """The standard part of the round, directly after a reset or a hit.
           External logic makes sure this repeats until _done = True is returned
           Once the player stands the torch is passed over to the dealer

        Args:
            action (str): Whether the player hits or stands ("hit" or "stand")

        Raises:
            RuntimeError: Game is already done, we should't be here
            ValueError: Something other than "hit" or "stand" was passed as an action

        Returns:
            Tuple[BJState, int, bool, dict[str, Any]]: _description_
        """
        if self._done:
            raise RuntimeError("Game is already done, please reset the environment")

        if action not in ("hit", "stand"):
            # IIRC i've set it up so only one of the 2 can be returned
            raise ValueError(f"Invalid action: {action}, must be 'hit' or 'stand'")

        reward = _DRAW  # default

        # ~~~~~~~~~~ player action ~~~~~~~~~~ #
        if action == "hit":
            card = self.deck.draw(1)[0]
            self.player.hand.add_cards([card])
            self._add_visible(card)

            if self.player.hand.is_bust():
                reward = _LOSE
                self._done = True

            elif self.player.hand.is_blackjack():
                # technically this is wrong, if both parties have a BJ it should draw
                # I probably should force a dealer action here to resolve this
                # chance of this happening is 0.177%, shouldn't effect model performance
                reward = _WIN
                self._done = True

        # ~~~~~~~~~~ dealer action ~~~~~~~~~~ #
        elif action == "stand":
            self._dealer_turn()
            reward = self._resolve_reward()
            self._done = True

        self._last_state = self._encode_state()
        if self._done:
            #pass
            print(f"Player total: {self.player.hand.hand_value}, dealer total: {self.dealer.hand.hand_value}, reward: {reward}")
        return (self._last_state, reward, self._done, {})

    def _dealer_turn(self) -> None:
        """Implements the dealer's flow (logic is handled in decide()). First reveals the hole card,
           then plays until he stands or busts.

        Raises:
            RuntimeError: This is called only onece, after the player stands, so there should always be a hole card
        """
        # reveal hole card
        card = self.dealer.hole_card
        if card is None:
            raise RuntimeError("Dealer's hole card is missing, debug")
        self.dealer.hand.add_cards([card])
        self._add_visible(card)
        self.dealer.hole_card = None

        # policy based .decide() loop
        while True:
            total, soft = self.dealer.hand.hand_value, self.dealer.hand.is_soft
            # we only really care about total and soft, can prob remove other values, might piss off BJState definition
            dealer_state = BJState(
                player_total=None,
                dealer_up=self._dealer_up_value,
                player_soft=None,
                count_bin=self._bin_count(),  # could be None?
                dealer_total=total,
                dealer_soft=soft,
            )
            action = self.dealer.policy.decide(dealer_state)
            if action == "stand":
                # game ends pretty much
                break
            card = self.deck.draw(1)[0]
            self.dealer.hand.add_cards([card])
            self._add_visible(card)
            if self.dealer.hand.is_bust():
                # dealer busts, player wins
                break
            elif self.dealer.hand.is_blackjack():
                # dealer has a blackjack, player loses
                break

    def _resolve_reward(self) -> int:
        """Once a game ending event has transpired (player/dealer bj/bust/+stand), this function decides who won.
           Standard bj rules apply, but I should probably add in the double bj logic. Some other time

        Returns:
            int: _description_
        """
        player_bust = self.player.hand.is_bust()
        dealer_bust = self.dealer.hand.is_bust()

        if player_bust:
            return _LOSE
        if dealer_bust:
            return _WIN

        player_value = self.player.hand.hand_value
        dealer_value = self.dealer.hand.hand_value

        if player_value > dealer_value:
            return _WIN
        if player_value < dealer_value:
            return _LOSE
        return _DRAW


if __name__ == "__main__":
    """Small demo
    """
    from blackjack_solver_simple.agents.policies import RandomPolicy

    env = BlackJackEnv(player_policy=RandomPolicy())
    state = env.reset()
    print("\nNew round --------------------------------")
    print("Initial state:", state)

    done = False
    reward = 0
    while not done:
        action = env.player.decide(state)
        print(f"> Player action: {action}")
        state, reward, done, _ = env.step(action)
        print("  New state:", state)

    outcome = {1: "WIN", 0: "DRAW", -1: "LOSE"}[reward]
    print(f"\n🏁 Round finished — player {outcome} (reward {reward})\n")
