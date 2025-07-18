# from src import GameGenerator

# if __name__ == "__main__":
#     game = GameGenerator(winscore=10)
#     print("Game played successfully.")
#     # Additional game logic can be added here

from src import MusEnv
from src import DQNAgent
import numpy as np

#rules: 3 and 2 are just that, not king and ace. 
# its 1v1 only grande, 
# there is only bet or pass, no raise or bet after the other passes. 
env = MusEnv()
state_size = 4  # 4 cards + 4 history inputs
action_size = 4  # fold, pass, small bet, big bet
agent = DQNAgent(state_size, action_size)

episodes = 1000
for ep in range(episodes):
    state = env.reset()
    done = False

    while not done:
        action = agent.select_action(state)
        next_state, reward, done = env.step(action)
        agent.store(state, action, reward, next_state, done)
        state = next_state

    agent.train()
    if ep % 10 == 0:
        agent.update_target()
        agent.epsilon *= 0.995  # decay epsilon
        print(f"Episode {ep} done")

