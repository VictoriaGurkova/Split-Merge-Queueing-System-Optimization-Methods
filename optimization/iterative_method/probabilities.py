import numpy as np


def get_probabilities(generator):
    n = len(generator[0])
    prob = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            prob[i][j] = 0 if i == j else generator[i][j] / (-generator[i][i])

    return prob
