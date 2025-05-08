from __future__ import annotations
import argparse
import random

from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.agents.policies import RandomPolicy
from blackjack_solver_simple.ui.human_cli import HumanCliPolicy

# ---------------------------------------------------------------------
# Helper: run ONE round and return reward
# ---------------------------------------------------------------------


def run_episode(env: BlackJackEnv) -> int:
    state = env.reset()
    done = False
    while not done:
        action = env.player.decide(state)
        state, reward, done, _ = env.step(action)
    return reward

# ---------------------------------------------------------------------
# Pretty helpers
# ---------------------------------------------------------------------


def _fmt_hand(hand) -> str:
    """Render a hand like '[A♠ 7♥] = 18 (soft)'. """
    cards_str = " ".join(str(c) for c in hand.cards)
    return f"[{cards_str}] = {hand.hand_value}{' (soft)' if hand.is_soft else ''}"


def _banner(text: str) -> None:
    print(f"\n{text}\n" + "-" * len(text))

# ---------------------------------------------------------------------
# Interactive episode runner (prints every step)
# ---------------------------------------------------------------------


def play_human(rng_seed: int | None) -> None:
    rng = random.Random(rng_seed)
    env = BlackJackEnv(player_policy=HumanCliPolicy(), rng=rng)

    state = env.reset()
    _banner("New round")
    print("Dealer shows :", env.dealer.hand.cards[0])
    print("Your hand     :", _fmt_hand(env.player.hand))

    # ---- Player loop ----
    done = False
    while not done:
        action = env.player.decide(state)          # input()
        print(f"\n> You choose to {action.upper()}")

        state, reward, done, _ = env.step(action)

        if action == "hit":
            new_card = env.player.hand.cards[-1]
            print("  You draw    :", new_card)
            print("  Your hand   :", _fmt_hand(env.player.hand))
            if done:
                break
        else:
            break  # stand → dealer turn handled inside env.step()

    # ---- Dealer reveal & play already happened if you stood ----
    if env.dealer.hole_card is None:              # hole has been revealed
        _banner("Dealer's final hand")
        print("Dealer hand   :", _fmt_hand(env.dealer.hand))

    # ---- Outcome ----
    outcome = {1: "WIN", 0: "DRAW", -1: "LOSE"}[reward]
    _banner(f"Result: you {outcome} (reward {reward})")


def play_random(episodes: int, rng_seed: int | None) -> None:
    rng = random.Random(rng_seed)
    env = BlackJackEnv(player_policy=RandomPolicy(), rng=rng)
    wins = draws = losses = 0
    for _ in range(episodes):
        r = run_episode(env)
        if r == 1:
            wins += 1
        elif r == 0:
            draws += 1
        else:
            losses += 1
    print("\n=== Random Policy vs Dealer ===")
    print(f"Episodes: {episodes}")
    print(f"Wins: {wins}  Draws: {draws}  Losses: {losses}")
    print(f"Win %: {wins / episodes * 100:.2f}")


# ~~~~~~~~~~ argparsing ~~~~~~~~~~~~ #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Blackjack RL project driver")
    p.add_argument("--mode", choices=("human", "random"), required=True,
                   help="Run mode: human (CLI play) or random (random policy).")
    p.add_argument("--episodes", type=int, default=10,
                   help="Episodes for --mode random (default 10).")
    p.add_argument("--seed", type=int, default=None,
                   help="Optional RNG seed for reproducibility.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "human":
        play_human(args.seed)
    elif args.mode == "random":
        play_random(args.episodes, args.seed)


if __name__ == "__main__":
    main()
