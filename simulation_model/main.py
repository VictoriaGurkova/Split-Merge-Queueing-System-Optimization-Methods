from model_properties.network_params import Params
from network_simulation import SplitMergeSystem
from policy.selection_policy import DefaultSelectionPolicy
from policy.states_policy import get_policed_states, get_all_possible_policies, Policy
from progress_bar import ConsoleProgressBar
from states.states_generator import get_all_states
import random


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
    policy_function = Policy(selected_policy_vector, states_with_policy, params).get_action_for_state
    for state in states_with_policy:
        print(f"    state = {state}, action = {policy_function(state)}")

    bar = ConsoleProgressBar('Progress: ')
    model = SplitMergeSystem(params, bar,
                             policy_function)
    simulation_time = 10_000
    statistics = model.run(simulation_time)

    print(statistics)


if __name__ == '__main__':
    random.seed(0)
    example1(2 ** 20 - 1)
