from pprint import pprint

from analytical_calculations.generator import create_generator
from model_properties.network_params import Params
from optimization.iterative_method.probabilities import get_probabilities
from optimization.iterative_method.reward import get_rewarded_for_states, get_income_matrix
from policy.states_policy import Policy, get_policed_states, get_strategy
from states.states_generator import get_all_states

if __name__ == '__main__':
    params = Params(mu=3, lambda1=1, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[1, 1])

    all_states = get_all_states(params)
    print(all_states)
    rewards = get_rewarded_for_states(all_states)
    print(rewards)

    states_with_policy = get_policed_states(all_states, params)
    strategies = get_strategy(states_with_policy)
    states_policy = Policy(tuple(), states_with_policy, params)

    states_policy.strategy = strategies[0]  # (0, 0, 0, 0)
    Q = create_generator(all_states, states_policy, params)
    q = get_income_matrix(rewards, Q)
    pprint(q)

    p = get_probabilities(Q)

    print("executed")
