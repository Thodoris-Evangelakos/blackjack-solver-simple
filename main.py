from __future__ import annotations
import argparse
import random
import numpy as np
import pickle
import gzip
import math

from configs.hypermarameters import ALPHA, INITIAL_EPSILON, GAMMA

from blackjack_solver_simple.core.env import BlackJackEnv
from blackjack_solver_simple.agents.policies import RandomPolicy, TabularQPolicy
from blackjack_solver_simple.ui.human_cli import HumanCliPolicy

TABLE_DIRECTORY = "tables/"

# ---------------------------------------------------------------------
# Helper: run ONE round and return reward
# ---------------------------------------------------------------------


def run_episode(env: BlackJackEnv) -> int:
    state = env.reset()
    done = False
    while not done:
        action = env.player.decide(state)
        state, reward, done, _ = env.step(action)
    return reward  # type: ignore

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
    outcome = {1: "WIN", 0: "DRAW", -1: "LOSE"}[reward]  # type: ignore
    _banner(f"Result: you {outcome} (reward {reward})")  # type: ignore


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


'''def _phase_1_state_conversion(state: BJState) -> BJStateQ:
    player_total, dealer_up, player_soft, _, _, _ = state
    return BJStateQ(player_total, dealer_up, player_soft)'''


def _calculate_epsilon(episode: int) -> float:
    # probably assuming initial epsilon == 1 (?)
    return (min(1.0, (2 * np.log(episode + 1))**(1/3) / (episode + 1)**(1/3)))


# I don't really like the idea of exposing all of this to main.py, looks really messy
def train_agent(episodes: int, rng_seed: int | None, counting_enabled, table_path: str) -> None:
    table_path = f"{TABLE_DIRECTORY}{table_path}.pkl.gz"
    rng = random.Random(rng_seed)
    policy = TabularQPolicy(learning_rate=ALPHA, initial_epsilon=INITIAL_EPSILON, gamma=GAMMA, counting_enabled=counting_enabled)
    env = BlackJackEnv(player_policy=policy, rng=rng)

    for ep in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = env.player.decide(state)
            next_state, reward, done, _ = env.step(action)
            # attempting to encode the state as a string for use as a dictionary key
            # this is a bit of a hack, but it works
            policy._update(state, action, reward, done, next_state)
            state = next_state
        policy.epsilon = _calculate_epsilon(ep)

    print(table_path)
    with gzip.open(table_path, "wb") as f:
        pickle.dump(policy.q_values, f)
    print(f"Q-table saved to {table_path}")


def eval_agent(episodes: int, rng_seed: int | None, counting_enabled, table_path: str) -> None:
    table_path = f"{TABLE_DIRECTORY}{table_path}.pkl.gz"

    with gzip.open(table_path, "rb") as f:
        q_table = pickle.load(f)

    policy = TabularQPolicy(
        learning_rate=0.0,
        initial_epsilon=0.0,
        gamma=1.0,
        counting_enabled=counting_enabled,
    )
    policy.q_values = q_table
    env = BlackJackEnv(player_policy=policy, rng=random.Random(rng_seed))

    wins = 0
    for ep in range(episodes):
        state = env.reset()
        done = False
        while not done:
            action = env.player.decide(state)
            state, reward, done, _ = env.step(action)
        if reward == 1:  # reset never ever returns done == True # type: ignore
            wins += 1

    p_hat = wins / episodes
    ci_half = 1.96 * math.sqrt(p_hat * (1 - p_hat) / episodes)
    print("\n=== Evaluation greedy agent ===")
    print(f"Episodes     : {episodes:,}")
    print(f"Wins         : {wins:,}")
    print(f"Win-rate     : {p_hat*100:.2f} %")
    print(f"95 % CI      : ({(p_hat-ci_half)*100:.2f} %, {(p_hat+ci_half)*100:.2f} %)")


# ~~~~~~~~~~ argparsing ~~~~~~~~~~~~ #
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Blackjack RL project driver")
    p.add_argument(
        "--mode",
        choices=("human", "random", "train", "eval"),
        required=True,
        help="Run mode: human, random, train, eval."
    )
    p.add_argument(
        "--interface",
        choices=("cli", "gui"),
        default="cli",
        help="UI interface to use when mode=human (cli or gui)."
    )
    p.add_argument(
        "--count",
        action="store_true",
        help="If set, allow card counting in the environment."
    )
    p.add_argument("--episodes", type=int, default=10,
                   help="Episodes for --mode random (default 10).")
    p.add_argument("--model", type=str, default="default_table",
                   help="Path to q table to load ")
    p.add_argument("--seed", type=int, default=None,
                   help="Optional RNG seed for reproducibility.")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "human":
        play_human(
            rng_seed=args.seed
            #interface=args.interface, # noqa e265
        )
    elif args.mode == "random":
        play_random(
            episodes=args.episodes,
            rng_seed=args.seed,
        )
    elif args.mode == "train":
        train_agent(
            episodes=args.episodes,
            rng_seed=args.seed,
            counting_enabled=args.count,
            table_path=args.model,
        )
    elif args.mode == "eval":
        eval_agent(
            episodes=args.episodes,
            rng_seed=args.seed,
            counting_enabled=args.count,
            table_path=args.model,
        )


if __name__ == "__main__":
    main()
