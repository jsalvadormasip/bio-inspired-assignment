import numpy as np
import matplotlib.pyplot as plt
from itertools import combinations
from collections import defaultdict
from src import MusEnvFullRound as MusEnv
import pickle
# from tqdm import tqdm

# Define SARSA hyperparameters
alpha = 0.01      # learning rate
gamma = 0.9      # discount factor
initial_epsilon = 0.2    # exploration rate
min_epsilon = 0.01
epsilon_decay = 0.995
num_episodes = 500
number_of_cards = 1
# Actions: 0 = fold, 1 = bet
actions = [0, 1]

# All possible 4-card hands (combinations without repetition)
all_hands = list(combinations(range(1, 11), number_of_cards))  # 715 unique hands
import itertools

combinations = list(itertools.combinations_with_replacement(range(1, 11), number_of_cards))
print(len(combinations))
all_hands = combinations
print(len(all_hands), "unique hands generated.")
# print(all_hands)
# State encoding (same as before)
# def state_to_int(hand):
#     h = np.sort(hand) - 1
#     return h[0]*1000 + h[1]*100 + h[2]*10 + h[3]

# ε-greedy policy
def choose_action(state, Q, epsilon):
    if np.random.rand() < epsilon:
        return np.random.choice(actions)
    else:
        return np.argmax(Q[state])

# Initialize Q-table
Q = defaultdict(lambda: np.zeros(len(actions)))
# print(Q)
# SARSA training loop
q_deltas =[]
for ep in range(num_episodes):
    max_delta = 0
    epsilon = max(min_epsilon, initial_epsilon*(epsilon_decay**ep))
    print(np.ceil(ep/num_episodes*100), "%", end='\r')  # Progress indicator
    for index,hand in enumerate(all_hands):
        # print(f"Episode {ep/num_episodes*100},hand {index/len(all_hands)*100}", end='\r')
        musenv = MusEnv(number_of_cards=number_of_cards)
        musenv.mode = "train"  # Set mode to train
        musenv.reset()
        musenv.hand = hand
        state = musenv._get_state()

        action = choose_action(state, Q, epsilon)

        # One-step episode (Mus is short): step → observe → update
        next_state, reward, done = musenv.step(action)
        if not done: 
            next_action = choose_action(next_state, Q, epsilon)
            musenv.second_chance = True #triggers the second agent decision
            final_state, reward, done = musenv.step(next_action)
            
            # SARSA update for step 1 (first agent decision)
            old_q = Q[state][action].copy()
            Q[state][action] += alpha *(reward + gamma *Q[next_state][next_action]-Q[state][action])

            #Optional: update for step 2 aswell
            final_action = choose_action(final_state, Q, epsilon)
            old_q2 = Q[next_state][next_action]
            Q[next_state][next_action] += alpha * (reward + gamma * Q[final_state][final_action] - Q[next_state][next_action])
        else:
            #single -step episode
            next_action = choose_action(next_state, Q, epsilon)
            old_q = Q[state][action]
            Q[state][action] += alpha * (reward + gamma * Q[next_state][next_action] - Q[state][action])

        
        # next_action = choose_action(next_state, Q, epsilon)
        # old_q = Q[state][action].copy()
        # # SARSA update
        # Q[state][action] += alpha * (
        #     reward + gamma * Q[next_state][next_action] - Q[state][action]
        # )
        delta = abs(Q[state][action]-old_q)
        max_delta = max(max_delta,delta)
    q_deltas.append(max_delta)
    if ep % 100 == 0:
        print("Sample Q values")
        for s in list(Q.keys())[:5]:
            print(s, Q[s])
# Derive value function and optimal policy
V = {s: max(q_vals) for s, q_vals in Q.items()}
policy = {s: np.argmax(q_vals) for s, q_vals in Q.items()}  # 0 = fold, 1 = bet
with open("sarsa_policy.pkl", "wb") as f:
    pickle.dump(policy, f)

print(f"Trained on {len(Q)} unique states.")


plt.plot(q_deltas)
plt.xlabel("Episode")
plt.ylabel("Max Q-value change")
plt.title("Convergence of Q-values")
plt.grid(True)
plt.show()


# --- Value function plot (x = hand strength = sum of cards) ---
x = [sum(state[0]) for state in V.keys()]  # state[0] = hand tuple
y = [V[state] for state in V.keys()]
plt.figure()
plt.scatter(x, y, alpha=0.6)
plt.xlabel("Hand Strength (Sum of 4 Cards)")
plt.ylabel("V(s) = max_a Q(s,a)")
plt.title("SARSA Value Function Estimates")
plt.grid(True)
plt.show()

# --- Policy plot (x = hand strength, y = action) ---
policy_vals = [policy[state] for state in V.keys()]  # 0 = fold, 1 = bet


plt.figure()
plt.scatter(x, policy_vals, alpha=0.6)
plt.xlabel(f"Hand Strength (Sum of {number_of_cards} Cards)")
plt.ylabel("Optimal Action (0=Fold, 1=Bet)")
plt.title("Optimal Policy Learned via SARSA")
plt.yticks([0, 1], labels=["Fold", "Bet"])
plt.grid(True)
plt.show()