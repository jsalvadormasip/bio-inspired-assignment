from src import MusEnvFullRound as MusEnv
import pickle
policy_path="sarsa_policy.pkl"
with open(policy_path, "rb") as f:
    policy = pickle.load(f)

def get_action_from_policy(state, policy=policy):
    return policy.get(state, 0)  # Default to 0 (fold) if state not found

musenv = MusEnv()

human_score = 0
machine_score = 0

while human_score < 10 and machine_score < 10:
    musenv.reset()
    state = musenv._get_state()

    action = get_action_from_policy(state)
    next_state, reward, done = musenv.step(action)
    if not done: 
        musenv.second_chance = True
        action = get_action_from_policy(next_state)
        next_state, reward, done = musenv.step(action)

    if reward > 0:
        machine_score += reward
    elif reward < 0:
        human_score -= reward
    else:
        print("No points awarded this round, bc it is a tie.")
    print(f" Human score = {human_score}, Machine score = {machine_score}")
    print("\n")
    print("\n")