import numpy as np

from calculations import Calculations
from model_properties.network_params import Params
from performance_measures import PerformanceMeasuresStorage
from policy.states_policy import Policy, get_policed_states
from states.states_generator import get_all_states

import matplotlib.pyplot as plt


def example1(lambdas, queue_id):
    storage = PerformanceMeasuresStorage()
    for lambd in lambdas:
        params = Params(mu=3, lambda1=lambd, lambda2=lambd,
                        servers_number=5,
                        fragments_numbers=[2, 3],
                        queues_capacities=[3, 3])

        all_states = get_all_states(params)
        states_with_policy = get_policed_states(all_states, params)

        selected_policy_vector = [queue_id] * len(states_with_policy)

        policy = Policy(selected_policy_vector, states_with_policy, params)

        calculations = Calculations(params)
        calculations.calculate(policy)
        performance_measures = calculations.performance_measures
        print(performance_measures, "\n")

        storage.append(lambd, performance_measures)

    print(storage)
    print()
    storage.show_difference()

    plt.title("Зависимость T от интенсивности входящего потока")
    plt.xlabel("lambdas")
    plt.ylabel("T")
    plt.grid()
    plt.plot(lambdas, storage.response_times, 'g', linewidth=2, markersize=12)
    plt.show()

    plt.title("Зависимость T1 и T2 от интенсивности входящего потока")
    plt.xlabel("lambdas")
    plt.ylabel("T")
    plt.grid()
    plt.plot(lambdas, storage.response_times1, 'g', label="T1", linewidth=2, markersize=12)
    plt.plot(lambdas, storage.response_times2, 'b', label="T2", linewidth=2, markersize=12)
    plt.legend()
    plt.show()

    plt.title("Зависимость pf от интенсивности входящего потока")
    plt.xlabel("lambdas")
    plt.ylabel("pf")
    plt.grid()
    plt.plot(lambdas, storage.blocked_all_queues_probability, 'b', linewidth=2, markersize=12)
    plt.show()

    plt.title("Зависимость pf1 и pf2 от интенсивности входящего потока")
    plt.xlabel("lambdas")
    plt.ylabel("pf")
    plt.grid()
    plt.plot(lambdas, storage.failure_probabilities1, 'g', label="pf1", linewidth=2, markersize=12)
    plt.plot(lambdas, storage.failure_probabilities2, 'b', label="pf2", linewidth=2, markersize=12)
    plt.legend()
    plt.show()


if __name__ == '__main__':
    lambdas = np.linspace(1, 5, num=9)

    example1(lambdas, queue_id=0)  # когда берем только из первой очереди
    example1(lambdas, queue_id=1)  # когда берем только из второй очереди

