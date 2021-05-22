import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from simulation_model.network_simulation import SplitMergeSystem
from states.states_generator import get_all_states


class QLearning:
    def __init__(self, model: SplitMergeSystem, state_with_policy: list,
                 learning_rate=0.9, reward_decay=0.9, e_greedy=0.9):
        self.model = model
        self.state_with_policy = state_with_policy
        self.actions = model.actions
        self.lr = learning_rate
        self.gamma = reward_decay
        self.epsilon = e_greedy
        self.q_table = pd.DataFrame(columns=self.actions, dtype=np.float64)
        self.q_table_final = pd.DataFrame(columns=self.actions, dtype=np.float64)

    def choose_action(self, observation):
        observation = str(observation)
        self.check_state_exist(observation)
        if np.random.uniform() < self.epsilon:
            state_action = self.q_table.loc[observation, :]
            state_action = state_action.reindex(np.random.permutation(state_action.index))
            action = state_action.idxmax()
        else:
            action = np.random.choice(self.actions)
        return action

    def learn(self, state, action, reward, next_state):
        state = str(state)
        next_state = str(next_state)
        self.check_state_exist(next_state)

        q_predict = self.q_table.loc[state, action]

        q_target = reward + self.gamma * self.q_table.loc[next_state, :].max()

        self.q_table.loc[state, action] += self.lr * (q_target - q_predict)

        return self.q_table.loc[state, action]

    def check_state_exist(self, state):
        state = str(state)
        if state not in self.q_table.index:
            self.q_table = self.q_table.append(
                pd.Series(
                    [0] * len(self.actions),
                    index=self.q_table.columns,
                    name=state,
                )
            )

    def print_q_table(self, all_states):
        for i in range(len(all_states)):
            state = str(all_states[i])
            for j in range(len(self.q_table.index)):
                if self.q_table.index[j] == state:
                    self.q_table_final.loc[state, :] = self.q_table.loc[state, :]

        print()
        print('Length of final Q-table =', len(self.q_table_final.index))
        print('Final Q-table with values from the final route:')
        print(self.q_table_final)

        print()
        print('Length of full Q-table =', len(self.q_table.index))
        print('Full Q-table:')
        print(self.q_table)

    def loop(self, episodes=10):
        steps = []
        costs = []
        for _ in range(episodes):
            step = 0
            cost = 0
            state = self.model.reset()

            while True:
                if self.is_it_possible_to_make_a_choice(state):
                    action = self.choose_action(state)
                    new_state, reward, done = self.model.step(action)
                    step += 1
                    cost += self.learn(state, action, reward, new_state)
                else:
                    new_state, reward, done = self.model.step()

                state = new_state

                if done:
                    steps += [step]
                    costs += [cost]
                    break

        self.print_q_table(get_all_states(self.model.get_params()))
        self.plot_results(steps, costs)

    def is_it_possible_to_make_a_choice(self, state: list):
        all_queue_not_empty = state[0][0] and state[0][1]
        can_any_class_to_occupy_servers = self.model.can_any_class_to_occupy_servers()
        return all_queue_not_empty and can_any_class_to_occupy_servers

    @staticmethod
    def plot_results(steps, cost):
        f, (ax1, ax2) = plt.subplots(nrows=1, ncols=2)
        ax1.plot(np.arange(len(steps)), steps, 'b')
        ax1.set_xlabel('Episode')
        ax1.set_ylabel('Steps')
        ax1.set_title('Episode via steps')

        ax2.plot(np.arange(len(cost)), cost, 'r')
        ax2.set_xlabel('Episode')
        ax2.set_ylabel('Cost')
        ax2.set_title('Episode via cost')

        plt.tight_layout()

        plt.figure()
        plt.plot(np.arange(len(steps)), steps, 'b')
        plt.title('Episode via steps')
        plt.xlabel('Episode')
        plt.ylabel('Steps')

        plt.figure()
        plt.plot(np.arange(len(cost)), cost, 'r')
        plt.title('Episode via cost')
        plt.xlabel('Episode')
        plt.ylabel('Cost')

        plt.show()
