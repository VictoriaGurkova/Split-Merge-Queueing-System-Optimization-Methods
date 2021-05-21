from model_properties.network_params import Params
from simulation_model.network_simulation import SplitMergeSystem
from simulation_model.progress_bar import ConsoleProgressBar
from states.states_generator import get_all_states

if __name__ == '__main__':
    params = Params(mu=3, lambda1=1.5, lambda2=1,
                    servers_number=5,
                    fragments_numbers=[2, 3],
                    queues_capacities=[1, 1])

    time = 10_000
    states = get_all_states(params)  # s
    actions = [0, 1]  # a
    rewards = []

    model = SplitMergeSystem(params=params, progress_bar=ConsoleProgressBar('Progress: '), simulation_time=time)



