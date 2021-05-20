import numpy as np
from oct2py import octave

from analytical_calculations.generator import create_generator
from model_properties.network_params import Params
from optimization.iterative_method.probabilities import get_probabilities
from optimization.reward import get_rewarded_for_states, get_income_matrix
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

        state_indices = [index for index, state in enumerate(self.all_states) if state in self.states_with_policy]
        print(state_indices)

        g, d = octave.iterative_method(self.all_states_num, state_indices, p, q, nout=2)
        stationary_strategy = list(map(int, d[0]))
        print("Оптимальный средний доход за один шаг:", g)
        print("Оптимальная стационарная стратегия:", stationary_strategy)

        for index, state in enumerate(self.states_with_policy):
            if stationary_strategy[index] == 1:
                print("После ухода из состояния", state, "брать требование из 1-ой очереди")
            elif stationary_strategy[index] == 2:
                print("После ухода из состояния", state, "брать требование из 2-ой очереди")

    def get_p(self):
        self.states_policy.strategy = self.strategies[0]
        generator = create_generator(self.all_states, self.states_policy, self.params)
        p1 = get_probabilities(generator)

        self.states_policy.strategy = self.strategies[-1]
        generator = create_generator(self.all_states, self.states_policy, self.params)
        p2 = get_probabilities(generator)

        return np.array([p1, p2])

    def get_q(self):
        rewards = get_rewarded_for_states(self.all_states)
        # для любой стратегии доход будет одинаковым
        self.states_policy.strategy = self.strategies[0]  # (0, 0, 0, 0)
        generator = create_generator(self.all_states, self.states_policy, self.params)
        q = get_income_matrix(rewards, generator)
        return q
