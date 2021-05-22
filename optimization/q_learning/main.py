from pprint import pprint

from model_properties.network_params import Params
from optimization.q_learning.agent import QLearning
from policy.states_policy import get_policed_states, Policy
from simulation_model.network_simulation import SplitMergeSystem
from simulation_model.progress_bar import ConsoleProgressBar
from states.states_generator import get_all_states

if __name__ == '__main__':
    # params = Params(mu=3, lambda1=1.5, lambda2=1,
    #                 servers_number=3,
    #                 fragments_numbers=[1, 2],
    #                 queues_capacities=[3, 3])

    params = Params(mu=3, lambda1=1.5, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[3, 3])

    time = 10_000
    states = get_all_states(params)
    states_with_policy = get_policed_states(states, params)
    print("All states where policy is possible:")
    pprint(states_with_policy)

    states_policy = Policy(tuple(), states_with_policy, params)
    states_policy.print_adjacent_states()

    rewards = [1] * len(states)

    model = SplitMergeSystem(params=params, progress_bar=ConsoleProgressBar('->'), simulation_time=time)
    agent = QLearning(model, states_with_policy)
    agent.loop()

