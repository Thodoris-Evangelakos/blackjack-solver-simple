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