from model_properties.network_params import Params
from optimization.iterative_method.iterative_method import IterativeMethod
from policy.states_policy import Policy, get_policed_states
from states.states_generator import get_all_states


def get_state_reward(state: list):
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
    return income - penalty


def example1():
    params = Params(mu=3, lambda1=3, lambda2=3,
                    servers_number=6,
                    fragments_numbers=[2, 3],
                    queues_capacities=[2, 2])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    states_policy = Policy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    iterative = IterativeMethod(all_states, states_policy,
                                get_state_reward,
                                params)
    iterative.apply(print_iteration_results=True)

    print("executed")


if __name__ == '__main__':
    example1()
