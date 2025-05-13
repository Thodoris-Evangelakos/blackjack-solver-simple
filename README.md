# Blackjack Solver Simple

A minimal reinforcement‐learning‐based Blackjack solver written in Python.  
Supports human play (CLI), random policy simulation, Q‐learning training, and evaluation of learned policies—with optional Hi-Lo card counting.

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Installation](#installation)  
4. [Usage](#usage)  
   - [Human vs Dealer (CLI)](#human-vs-dealer-cli)  
   - [Random Policy Simulation](#random-policy-simulation)  
   - [Training a Q-Learning Agent](#training-a-q-learning-agent)  
   - [Evaluating a Trained Agent](#evaluating-a-trained-agent)  
5. [Project Structure](#project-structure)  
6. [Testing](#testing)  
7. [Configuration](#configuration)  
8. [License](#license)

---

## Features

- **Human Play (CLI)**  
- **Random Policy Benchmarking**  
- **Tabular Q-Learning** with ε-greedy exploration  
- **Hi-Lo Card Counting** toggle  
- **Save/Load Q-tables** (`.pkl.gz`)  
- **Built-in Unit Tests** (pytest)

## Prerequisites

- Python 3.10+  
- `pip` (or `poetry`)  
- Git (optional)

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/blackjack-solver-simple.git
cd blackjack-solver-simple

# (optional) create a venv
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Usage

All entrypoints are in the project root. Replace `<N>` and `<TABLE_NAME>` as desired.

### Human vs Dealer (CLI)

```bash
python main.py --mode human
```

Add `--count` to enable Hi-Lo counting.

### Random Policy Simulation

```bash
python main.py --mode random --episodes 1000 --seed 42
```

### Training a Q-Learning Agent

```bash
python main.py \
  --mode train \
  --episodes 50000 \
  --model my_q_table \
  --count \
  --seed 123
```

- Outputs `tables/my_q_table.pkl.gz`

### Evaluating a Trained Agent

```bash
python main.py \
  --mode eval \
  --episodes 10000 \
  --model my_q_table \
  --count \
  --seed 999
```

## Project Structure

```
.
├── configs/              # hyperparameters
│   └── hypermarameters.py
├── src/blackjack_solver_simple/
│   ├── core/             # game engine, deck, hand, state, env
│   ├── agents/           # policies: Random, Q-learning, Dealer
│   └── ui/               # CLI & (future) GUI
├── tables/               # saved Q-tables (.pkl.gz)
├── tests/                # pytest suite
│   └── core/             # unit tests for card, deck, hand, env
├── main.py               # CLI driver
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Testing

Run the full test suite with:

```bash
pytest
```

Or target a single module:

```bash
pytest test_env.py
```

## Configuration

All learning hyperparameters are in [`configs/hypermarameters.py`](configs/hypermarameters.py):

```python
ALPHA = 0.1
INITIAL_EPSILON = 1.0
GAMMA = 1
```

## License

TUC © Thodoris Evangelakos, Harry Houlis