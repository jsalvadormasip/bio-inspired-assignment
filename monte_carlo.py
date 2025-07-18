import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict
from src import MusEnv

# Initialize value function and return memory
V = {}
Returns = defaultdict(list)

# All possible 4-card hands from 1 to 10 (no order, no suit)
all_hands = list(combinations(range(1, 11), 4))  # 715 hands
print(len(all_hands), "unique hands generated.")
# def state_to_int(hand):
#     """Encode hand as unique integer (sorted digits 0–9)."""
#     h = np.sort(hand) - 1
#     return h[0]*1000 + h[1]*100 + h[2]*10 + h[3]

def choose_action(hand):
    """Simple baseline agent: bet if hand strength is good."""
    return np.random.choice([0,1])

# Training loop
for ep in range(200):  # Repeat to average results
    for hand in all_hands:
        musenv = MusEnv()
        musenv.reset()
        musenv.hand = hand
        # state = musenv._get_state()
        action = choose_action(hand)
        state, reward, _ = musenv.step(action)
        
        if state not in Returns:
            Returns[state] = []
        
        Returns[state].append(reward)
        V[state] = np.mean(Returns[state])

print(f"Trained on {len(V)} unique hands (should be 210)")

# Plotting value vs hand strength
def decode_state(state):
    """Convert encoded state back to hand tuple for plotting."""
    a = state // 1000
    b = (state % 1000) // 100
    c = (state % 100) // 10
    d = state % 10
    return (a, b, c, d)

x = [k for k in V.keys()]  # Hand strength
y = [v for v in V.values()]

plt.plot(x, y)
plt.xlabel("Cards")
plt.ylabel("Estimated Value")
plt.title("Monte Carlo Value Estimates (All 715 Hands)")
plt.grid(True)
plt.show()
