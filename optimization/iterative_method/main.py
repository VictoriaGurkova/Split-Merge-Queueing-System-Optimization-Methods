from model_properties.network_params import Params
from optimization.iterative_method.iterative_method import IterativeMethod
from policy.states_policy import Policy, get_policed_states
from states.states_generator import get_all_states

if __name__ == '__main__':
    params = Params(mu=3, lambda1=1, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[3, 2])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    states_policy = Policy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    iterative = IterativeMethod(all_states, states_policy, params)
    iterative.apple()

    print("executed")
