import math

import numpy as np
from scipy.linalg import solve

from analytical_calculations.calculations import Calculations
from analytical_calculations.generator import create_generator
from model_properties.network_params import Params
from optimization.iterative_method.probabilities import get_probabilities
from optimization.iterative_method.reward import get_rewards_for_states, get_income_matrix
from policy.states_policy import Policy


class IterativeMethod:

    def __init__(self, all_states: list, states_policy: Policy,
                 reward_function_for_states,
                 params: Params):
        self.all_states = all_states
        self.all_states_num = len(all_states)
        self.states_with_policy = states_policy.states_with_policy
        self.states_with_policy_num = states_policy.states_with_policy_num
        self.states_policy = states_policy
        self.params = params
        self._reward_function_for_states = reward_function_for_states

        self._zeros_policy: list = [0] * self.states_with_policy_num
        self._ones_policy: list = [1] * self.states_with_policy_num

    def run(self, P, q,
            state_ids_with_policy,
            n_states,
            n_states_with_policy,
            max_iter, print_iteration_results):

        pred_g = float('inf')
        policy_vector = np.array([0] * n_states_with_policy)

        for iter in range(max_iter):
            P_policy = []
            q_policy = []
            for s in range(n_states):
                action = 0
                if s in state_ids_with_policy:
                    id = state_ids_with_policy.index(s)
                    action = policy_vector[id]
                P_policy.append(P[action][s])
                q_policy.append(q[action][s])

            P_policy = np.vstack(P_policy)
            q_policy = np.array(q_policy)

            P_policy = P_policy - np.eye(P_policy.shape[0])
            P_policy[:, -1] = -1

            x = solve(P_policy, -q_policy)

            v = list(x[:-1])
            v.append(0)
            v = np.array(v)

            g = x[-1]

            v_pred = np.copy(v)
            new_policy_vector = np.copy(policy_vector)
            for id, s in enumerate(state_ids_with_policy):
                criterion = [q[0][s] + np.dot(P[0][s], v_pred),
                             q[1][s] + np.dot(P[1][s], v_pred)]
                # print('vi = ', vi)
                opt_action = np.argmax(criterion)
                new_policy_vector[id] = opt_action

            if (print_iteration_results):
                print('-' * 200)
                print(f'ITERATION:{iter}')

                print(f"Policy at iter {iter} = {policy_vector}")

                stationary_strategy = policy_vector
                print("Optimal average income per step:", g)
                print("Optimal stationary strategy:", stationary_strategy)

                calculations = Calculations(self.params)
                policy = Policy(stationary_strategy, self.states_with_policy, self.params)
                calculations.calculate(policy)
                performance_measures = calculations.performance_measures
                print(performance_measures, "\n")

                print('-' * 200)

            if np.all(new_policy_vector == policy_vector):
                print('SUCCESS: policies were the same')
                return g, policy_vector

            if math.isclose(g, pred_g, abs_tol=1e-15):
                print('SUCCESS: income the same')
                return g, policy_vector

            pred_g = g
            policy_vector = np.copy(new_policy_vector)

        print("MAX ITERATIONS!")
        return None

    def apply(self, print_iteration_results=True):

        p = self.get_p()
        q = self.get_q()

        state_indices = [index for index, state in enumerate(self.all_states)
                         if state in self.states_with_policy]
        print(state_indices)

        g, stationary_strategy = self.run(p, q, state_indices, self.all_states_num, self.states_with_policy_num,
                                          100000, print_iteration_results)

        print("Optimal average income per step:", g)
        print("Optimal stationary strategy:", stationary_strategy)

        for index, state in enumerate(self.states_with_policy):
            if stationary_strategy[index] == 0:
                print("After leaving the state", state, "take a demand from the 1st queue")
            elif stationary_strategy[index] == 1:
                print("After leaving the state", state, "take a demand from the 2st queue")

        calculations = Calculations(self.params)
        policy = Policy(stationary_strategy, self.states_with_policy, self.params)
        calculations.calculate(policy)
        performance_measures = calculations.performance_measures
        print(performance_measures, "\n")

    def get_p(self):
        self.states_policy.policy_vector = self._zeros_policy
        generator = create_generator(self.all_states, self.states_policy, self.params)
        p1 = get_probabilities(generator)

        self.states_policy.policy_vector = self._ones_policy
        generator = create_generator(self.all_states, self.states_policy, self.params)
        p2 = get_probabilities(generator)

        return np.array([p1, p2])

    def get_q(self):
        self.states_policy.policy_vector = self._zeros_policy
        generator1 = create_generator(self.all_states, self.states_policy, self.params)
        p1 = get_probabilities(generator1)

        self.states_policy.policy_vector = self._ones_policy
        generator2 = create_generator(self.all_states, self.states_policy, self.params)
        p2 = get_probabilities(generator2)

        rewards = get_rewards_for_states(self.all_states, self._reward_function_for_states)
        # for any strategy, the income will be the same
        r = get_income_matrix(rewards, generator1)

        q1 = []
        q2 = []
        for pi in p1:
            q1.append(np.dot(pi, r))
        for pi in p2:
            q2.append(np.dot(pi, r))

        return [q1, q2]
