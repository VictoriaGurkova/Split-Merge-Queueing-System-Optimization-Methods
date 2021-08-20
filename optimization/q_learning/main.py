from pprint import pprint

from model_properties.network_params import Params
from optimization.q_learning.agent import QLearning
from policy.states_policy import get_policed_states, Policy
from simulation_model.network_simulation import SplitMergeSystem
from simulation_model.progress_bar import ConsoleProgressBar
from states.states_generator import get_all_states


# просто штрафуем за нахождение отказ в обслуживании
def reward_function1(old_state, new_state, time_in_state):
    q1, q2 = old_state[0][0], old_state[0][1]

    penalty = q2 * time_in_state
    return -penalty


def reward_function2(state, new_state, time_in_state):
    q1, q2 = state[0][0], state[0][1]

    # за обслуживание требований каждого класса получаем доход
    income1 = 0.5
    income2 = 0.7
    income = income1 * len(state[1][0]) + income2 * len(state[1][1])

    # но не хотим, чтобы требования получали отказ
    # capacity здесь должно совпадать с той, что в системе!
    capacity1 = 2
    capacity2 = 2
    # penalty for failures (queue blocked)
    penalty = int(q2 == capacity2) + int(q1 == capacity1)

    # не забываем умножать на время в состоянии
    return (income - penalty) * time_in_state


if __name__ == "__main__":
    # params = Params(mu=3, lambda1=1.5, lambda2=1,
    #                 servers_number=3,
    #                 fragments_numbers=[1, 2],
    #                 queues_capacities=[3, 3])

    # params = Params(mu=3, lambda1=5, lambda2=5,
    #                 servers_number=6,
    #                 fragments_numbers=[3, 3],
    #                 queues_capacities=[2, 2])

    params = Params(
        mu=3,
        lambda1=3,
        lambda2=3,
        servers_number=6,
        fragments_numbers=[2, 3],
        queues_capacities=[2, 2],
    )

    states = get_all_states(params)
    states_with_policy = get_policed_states(states, params)
    print("All states where policy is possible:")
    pprint(states_with_policy)

    states_policy = Policy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    model = SplitMergeSystem(params=params, reward_policy=reward_function2)
    agent = QLearning(
        model,
        states_with_policy,
        reward_decay=1,
        learning_rate=0.3,
        e_greedy=0.1,
        progress_bar=ConsoleProgressBar("*"),
    )

    max_steps = 1_000_000
    agent.loop(max_steps, warming_duration=0.2)
