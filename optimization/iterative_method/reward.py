def get_rewarded_for_states(states: list):
    rewards = []
    for state in states:
        rewards.append(get_reward(state))

    return rewards


def get_reward(state: list):
    q1, q2 = state[0][0], state[0][1]
    servers_working_num = sum(state[1][0]) + sum(state[1][1])
    reward = q1 + q2 + servers_working_num
    return -reward


def get_income_matrix(rewards, generator):
    if len(rewards) != len(generator[0]):
        raise Exception('Length does not match')

    q = []
    for i in range(len(rewards)):
        q.append(rewards[i] * (-generator[i][i] ** (-1)))

    return q
