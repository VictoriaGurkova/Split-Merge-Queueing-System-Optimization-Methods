from model_properties.network_params import Params
from network_simulation import SplitMergeSystem
from policy.selection_policy import SelectionPolicy
from policy.states_policy import get_policed_states, get_strategy
from progress_bar import ConsoleProgressBar
from states.states_generator import get_all_states

if __name__ == '__main__':
    # this code initializes network parameters, starts statistics and performs simulation split-merge network
    params = Params(mu=3, lambda1=.5, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[1, 1])

    all_states = get_all_states(params)
    states_with_policy = get_policed_states(all_states, params)
    strategies = get_strategy(states_with_policy)

    SelectionPolicy.set_policy(strategies[0], states_with_policy, params)

    bar = ConsoleProgressBar('Progress: ')
    model = SplitMergeSystem(params, bar, SelectionPolicy.according_to_policy)

    simulation_time = 100
    statistics = model.run(simulation_time)

    print(statistics)
