from pprint import pprint

from calculations import Calculations
from model_properties.network_params import Params
from performance_measures import PerformanceMeasuresStorage
from policy.states_policy import Policy, get_policed_states, get_all_possible_policies
from states.states_generator import get_all_states


def example1(policy_id):
    params = Params(mu=3, lambda1=4, lambda2=4,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[3, 3])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    policies = get_all_possible_policies(states_with_policy)
    # print("All possible policies number: ", len(policies))

    selected_policy_vector = None
    for idx, p in enumerate(policies):
        selected_policy_vector = p
        if idx == policy_id:
            break

    print("Current policy:")
    policy = Policy(selected_policy_vector, states_with_policy, params)
    for state in states_with_policy:
        print(f"    state = {state}, action = {policy.get_action_for_state(state)}")

    calculations = Calculations(params)
    calculations.calculate(policy)
    performance_measures = calculations.performance_measures
    print(performance_measures, "\n")


def example5(policy_id):
    params = Params(mu=3, lambda1=5, lambda2=5,
                    servers_number=6,
                    fragments_numbers=[3, 3],
                    queues_capacities=[3, 3])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    policies = get_all_possible_policies(states_with_policy)
    # print("All possible policies number: ", len(policies))

    selected_policy_vector = None
    for idx, p in enumerate(policies):
        selected_policy_vector = p
        if idx == policy_id:
            break

    print("Current policy:")
    policy = Policy(selected_policy_vector, states_with_policy, params)
    for state in states_with_policy:
        print(f"    state = {state}, action = {policy.get_action_for_state(state)}")

    calculations = Calculations(params)
    calculations.calculate(policy)
    performance_measures = calculations.performance_measures
    print(performance_measures, "\n")


def example3(queue_id):
    params = Params(mu=3, lambda1=4, lambda2=4,
                    servers_number=6,
                    fragments_numbers=[3, 2],
                    queues_capacities=[3, 3])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)

    selected_policy_vector = [queue_id] * len(states_with_policy)

    print("Current policy:")
    policy = Policy(selected_policy_vector, states_with_policy, params)
    for state in states_with_policy:
        print(f"    state = {state}, action = {policy.get_action_for_state(state)}")

    calculations = Calculations(params)
    calculations.calculate(policy)
    performance_measures = calculations.performance_measures
    print(performance_measures, "\n")


def example4():
    print('See the fail_probs for example')
    print('Take from the first queue only')
    example3(0)
    print('Take from the second queue only')
    example3(1)


def example2():
    params = Params(mu=3, lambda1=5, lambda2=5,
                    servers_number=6,
                    fragments_numbers=[3, 2],
                    queues_capacities=[1, 1])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    print("All states where policy is possible:")
    pprint(states_with_policy)

    strategies = get_all_possible_policies(states_with_policy)
    states_policy = Policy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    storage = PerformanceMeasuresStorage()
    print()

    for strategy in strategies:
        states_policy.policy_vector = strategy
        print(strategy)
        calculations = Calculations(params)
        calculations.calculate(states_policy)
        performance_measures = calculations.performance_measures
        print(performance_measures, "\n")

        storage.append(strategy, performance_measures)

    print(storage)
    print()
    storage.show_difference()

    print("executed")


if __name__ == '__main__':
    # example1(2**20-1)
    # example1(1)

    example4()
