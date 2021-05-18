def get_rewarded_for_states(states: list):
    rewards = []
    for state in states:
        rewards.append(_get_reward(state))

    return rewards


def _get_reward(state: list):
    # вознаграждение за состояние считается по количеству требований в системе (минимизиурем их)
    reward = state[0][0] + state[0][1] + len(state[1][0]) + len(state[1][1])
    return -reward


def get_income_matrix(rewards, generator):
    if len(rewards) != len(generator[0]):
        raise Exception('Length does not match')

    q = []
    for i in range(len(rewards)):
        q.append(rewards[i] * (-generator[i][i] ** (-1)))

    return q
