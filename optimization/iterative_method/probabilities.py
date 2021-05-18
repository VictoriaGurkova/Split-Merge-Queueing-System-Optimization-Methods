def get_probabilities(generator):
    n = len(generator[0])

    prob = [0] * n
    for i in range(n):
        prob[i] = [0] * n

    for i in range(n):
        for j in range(n):
            prob[i][j] = 0 if i == j else generator[i][j] / (-generator[i][i])

    return prob
