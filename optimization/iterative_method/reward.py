def get_rewards_for_states(states: list, reward_function_for_states):
    rewards = []
    for state in states:
        rewards.append(reward_function_for_states(state))

    return rewards


def get_income_matrix(rewards, generator):
    if len(rewards) != len(generator[0]):
        raise Exception('Length does not match')

    q = []
    for i in range(len(rewards)):
        q.append(rewards[i] * (-1 / generator[i][i]))

    return q
