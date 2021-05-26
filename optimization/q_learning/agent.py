import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib

from policy.states_policy import get_policed_states
from simulation_model.network_simulation import SplitMergeSystem
from simulation_model.progress_bar import ProgressBar
from states.states_generator import get_all_states


class QLearning:
    def __init__(self, model: SplitMergeSystem, state_with_policy: list,
                 learning_rate=1, reward_decay=0.9, e_greedy=0.4,
                 progress_bar: ProgressBar = None):
        self.model = model
        self.state_with_policy = state_with_policy
        self.actions = model.actions
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self._progress_bar = progress_bar

        all_states = get_all_states(model.get_params())
        self._states_with_policy = get_policed_states(all_states, model.get_params())
        self.n_states_with_actions = len(self._states_with_policy)

        self._state_id_map = dict()
        for id, state in enumerate(self._states_with_policy):
            self._state_id_map[str(state)] = id

        self._n_actions = 2
        self.q_table = np.zeros((self.n_states_with_actions, self._n_actions))

    def action_for_state(self, state):
        state_id = self._get_state_id(state)
        action = np.argmax(self.q_table[state_id])
        return action

    def _get_state_id(self, state):
        return self._state_id_map[str(state)]

    def make_decision(self, state, choose_random=False):
        if choose_random:
            return np.random.choice(self._n_actions)
        if np.random.random() < self.epsilon:
            return np.random.choice(self._n_actions)
        else:
            return self.action_for_state(state)

    def update_quality_table(self, state, action, reward, next_state):
        state = str(state)
        next_state = str(next_state)
        state_id = self._get_state_id(state)
        new_state_id = self._get_state_id(next_state)

        q_current = self.q_table[state_id, action]
        q_target = reward + self.gamma * self.q_table[new_state_id].max()
        self.q_table[state_id, action] += self.lr * (q_target - q_current)

    def print_q_table(self):
        print()
        print('Length of Q-table =', len(self.q_table.shape))
        print('Q-table:')
        for state, state_qualities in zip(self._states_with_policy, self.q_table):
            print(f'{state}: \t {state_qualities}  -> {self.action_for_state(state)}')

        print('Policy:')
        print(self._get_current_policy())

    # warming_duration - percent of steps to warm up the simulation
    # in this phase we use random actions
    # and this way helps to fill Q-table with some appropriate initial values
    def loop(self, max_steps, warming_duration=0.1):
        times = [0]
        self.model._first_step()
        state = self.model._state_before_leaving
        accumulated_reward = [0]
        mean_reward_per_time = [accumulated_reward[-1] / self.model._times.current]

        for step in range(max_steps):
            if self._progress_bar:
                self._progress_bar.update_progress(float(step), max_steps)

            action = self.make_decision(state, step < max_steps * warming_duration)
            new_state, reward = self.model._big_step(action)

            # statistics
            times.append(self.model._times.current)
            accumulated_reward.append(accumulated_reward[-1] + reward)
            mean_reward_per_time.append(accumulated_reward[-1] / self.model._times.current)

            # print(state)
            # print(new_state)
            self.update_quality_table(state, action, reward, new_state)
            state = new_state

            if step % (max_steps // 100) == 0:
                print('')
                print(self._get_current_policy())



        # TO SAVE AS EPS
        # plt.rcParams['text.latex.preamble'] = [r'\usepackage{mathptmx}']  # load times roman font
        # plt.rcParams['font.family'] = 'serif'  # use serif font as default
        # plt.rcParams['text.usetex'] = True  # enable LaTeX rendering globally
        plt.style.use('seaborn-colorblind')
        plt.grid()

        self.print_q_table()
        plt.plot(times, accumulated_reward)
        plt.title('Accumulated reward')
        plt.show()
        #plt.savefig('check1.eps')

        plt.clf()
        plt.grid()
        # we plot only data after some period (warming_up_period/2)
        plt.plot(times[int(warming_duration * max_steps / 2):],
                 mean_reward_per_time[int(warming_duration * max_steps / 2):])
        plt.title('Mean reward per time')
        plt.show()
        #plt.savefig('check2.eps')

    def _get_current_policy(self):
        policy = []
        for state, state_qualities in zip(self._states_with_policy, self.q_table):
            policy.append(self.action_for_state(state))
        return policy

    def is_it_possible_to_make_a_choice(self, state: list):
        all_queue_not_empty = state[0][0] and state[0][1]
        can_any_class_to_occupy_servers = self.model.can_any_class_to_occupy_servers()
        return all_queue_not_empty and can_any_class_to_occupy_servers
