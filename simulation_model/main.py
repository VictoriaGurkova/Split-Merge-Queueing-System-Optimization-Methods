from pprint import pprint

from model_properties.network_params import Params
from network_simulation import SplitMergeSystem
from policy.states_policy import get_policed_states, get_strategy, StatesPolicy
from progress_bar import ConsoleProgressBar
from selection_policy import SelectionPolicy
from states.states_generator import get_all_states

if __name__ == '__main__':
    # this code initializes network parameters, starts statistics and performs simulation split-merge network
    params = Params(mu=3, lambda1=.5, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[1, 1])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    print("All states where policy is possible:")
    pprint(states_with_policy)

    strategies = get_strategy(states_with_policy)
    states_policy = StatesPolicy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    bar = ConsoleProgressBar('Progress: ')
    model = SplitMergeSystem(params, bar, SelectionPolicy.random_order)

    simulation_time = 100_000
    statistics = model.run(simulation_time)

    print(statistics)
