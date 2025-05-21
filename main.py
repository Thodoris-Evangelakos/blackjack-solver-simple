from __future__ import annotations
import argparse
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
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
            policy.rewards.append(reward)
        policy.epsilon = _calculate_epsilon(ep)

    print(table_path)
    with gzip.open(table_path, "wb") as f:
        pickle.dump(policy.q_values, f)
    print(f"Q-table saved to {table_path}")
    policy_visualization(policy)
    visualize_policy_tabular(policy, title="Greedy policy after training")


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

    policy_visualization(policy)
    visualize_policy_tabular(policy, title="Greedy policy after training")


def policy_visualization(policy: TabularQPolicy) -> None:
    rolling_window = 1000

    # Compute cumulative rewards and their rolling average
    cumsum_rewards = np.cumsum(policy.rewards)
    cum_rewards_smooth = pd.Series(cumsum_rewards).rolling(rolling_window).mean()

    # Compute the rolling average of the raw rewards per episode
    rewards_smoothed = pd.Series(policy.rewards).rolling(rolling_window).mean()

    # Compute smoothed training error
    training_error_smooth = pd.Series(policy.training_error_qlearning).rolling(rolling_window).mean()

    plt.figure(figsize=(18, 6))

    # Plot smoothed cumulative rewards
    plt.subplot(1, 3, 1)
    plt.plot(cum_rewards_smooth, label="Cumulative Rewards", color="blue")
    plt.title("Smoothed Cumulative Rewards")
    plt.xlabel("Episode")
    plt.ylabel("Cumulative Reward")
    plt.legend()

    # Plot temporal difference error smoothed with a 1000-episode window
    plt.subplot(1, 3, 2)
    plt.plot(training_error_smooth, label="TD Error", color="red", lw=1)
    plt.title("Smoothed Temporal Difference Error")
    plt.xlabel("Episode")
    plt.ylabel("Error")
    plt.legend()

    # Plot reward per episode, smoothed with the same rolling window
    plt.subplot(1, 3, 3)
    plt.plot(rewards_smoothed, label="Reward per Episode", color="green")
    plt.title("Smoothed Reward per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.legend()

    plt.tight_layout()
    plt.show()


def visualize_policy_tabular(
    policy: TabularQPolicy,
    *,
    player_min: int = 12,
    player_max: int = 21,
    dealer_min: int = 2,
    dealer_max: int = 11,
    title: str = "Learned greedy policy"
) -> None:
    """
    Draw heat-maps of the greedy action stored in `policy.q_values`.

    • 0 = hit   • 1 = stand   • 2 = state never visited  
    Colours: green (hit) ▸ black (stand) ▸ light-grey (no-data)

    If `policy.counting_enabled` is True we display one pair of
    heat-maps for each count_bin (-1, 0, +1).
    """
    # grid dimensions
    n_player = player_max - player_min + 1
    n_dealer = dealer_max - dealer_min + 1

    # decide how many columns we need
    count_bins = (-1, 0, +1) if policy.counting_enabled else (None,)
    ncols = len(count_bins)

    fig, axes = plt.subplots(
        2, ncols, figsize=(6 * ncols, 6), squeeze=False
    )

    cmap = mcolors.ListedColormap(["green", "black", "lightgrey"])
    norm = mcolors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5], cmap.N)

    for c_idx, c_bin in enumerate(count_bins):
        # default to “no-data”
        hard_grid = np.full((n_player, n_dealer), 2, dtype=int)
        soft_grid = np.full((n_player, n_dealer), 2, dtype=int)

        for i, p_sum in enumerate(range(player_min, player_max + 1)):
            for j, d_up in enumerate(range(dealer_min, dealer_max + 1)):
                for soft_flag, grid in ((False, hard_grid), (True, soft_grid)):
                    # build the state tuple exactly like the learner did
                    if policy.counting_enabled:
                        tpl = (p_sum, d_up, soft_flag, c_bin)
                    else:
                        tpl = (p_sum, d_up, soft_flag)
                    k = hash(tpl)
                    if k in policy.q_values:
                        grid[i, j] = int(np.argmax(policy.q_values[k]))

        # ── draw one column (hard / soft) ────────────────────────────
        for r, grid in enumerate((hard_grid, soft_grid)):
            ax = axes[r, c_idx]
            im = ax.imshow(grid, cmap=cmap, norm=norm,
                           origin="lower", aspect="auto")

            ax.set_title(
                f"{title}"
                + (f"\ncount_bin = {c_bin:+d}" if policy.counting_enabled else "")
                + (", soft hand" if r else ", hard hand")
            )
            ax.set_xlabel("Dealer up-card")
            ax.set_ylabel("Player total")
            ax.set_xticks(np.arange(n_dealer))
            ax.set_xticklabels(
                [str(x) if x != 11 else "A" for x in range(dealer_min, dealer_max + 1)]
            )
            ax.set_yticks(np.arange(n_player))
            ax.set_yticklabels(range(player_min, player_max + 1))

            # one colour-bar per subplot keeps things tidy
            cbar = fig.colorbar(im, ax=ax, ticks=[0, 1, 2])
            cbar.ax.set_yticklabels(["Hit (0)", "Stand (1)", "No data"])

    plt.tight_layout()
    plt.show()


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
