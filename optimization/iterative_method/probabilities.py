from pprint import pprint


def get_probabilities(Q):
    n = len(Q[0])

    prob = [0] * n
    for i in range(n):
        prob[i] = [0] * n

    for i in range(n):
        for j in range(n):
            prob[i][j] = 0 if i == j else Q[i][j] / (-Q[i][i])

    return prob
