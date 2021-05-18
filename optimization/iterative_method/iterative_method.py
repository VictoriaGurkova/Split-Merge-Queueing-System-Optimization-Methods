from oct2py import octave

from analytical_calculations.generator import create_generator
from model_properties.network_params import Params
from optimization.iterative_method.probabilities import get_probabilities
from optimization.iterative_method.reward import get_rewarded_for_states, get_income_matrix
from policy.states_policy import Policy, get_strategy


class IterativeMethod:

    def __init__(self, all_states: list, states_policy: Policy, params: Params):
        self.all_states = all_states
        self.all_states_num = len(all_states)
        self.states_with_policy = states_policy.states_with_policy
        self.states_with_policy_num = states_policy.states_with_policy_num
        self.states_policy = states_policy
        self.params = params

        self.strategies: list = get_strategy(self.states_with_policy)

    def apple(self):
        octave.cd(octave.pwd() + '/octave')

        p = self.get_p()
        q = self.get_q()
        g, d = octave.iterative_method(self.states_with_policy_num, p, q)

        print(g)
        print(d)

    def get_p(self):
        # TODO: что за вероятности должны быть?
        p = []
        for strategy in self.strategies:
            self.states_policy.strategy = strategy
            generator = create_generator(self.all_states, self.states_policy, self.params)
            p.append(get_probabilities(generator))

        return p

    def get_q(self):
        rewards = get_rewarded_for_states(self.all_states)
        self.states_policy.strategy = self.strategies[0]  # (0, 0, 0, 0)
        generator = create_generator(self.all_states, self.states_policy, self.params)
        return get_income_matrix(rewards, generator)
            







