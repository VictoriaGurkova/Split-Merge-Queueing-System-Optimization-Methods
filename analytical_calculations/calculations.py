from model_properties.network_params import Params
from analytical_calculations.performance_measures import PerformanceMeasures
from states.pretty_states import pretty_state
from states.states_generator import get_all_states


class Calculations:

    def __init__(self, params: Params) -> None:
        self.params = params
        self.performance_measures = PerformanceMeasures()

    def calculate(self, states_policy) -> None:
        from analytical_calculations.generator import get_stationary_distribution
        from analytical_calculations.logs import log_network_configuration, log_message

        log_network_configuration(self.params)
        states = get_all_states(self.params)

        distribution = get_stationary_distribution(states, states_policy, self.params)
        log_message(f'Stationary distribution P_i:\n {distribution}')
        log_message(f'Check sum P_i: {sum(distribution)}')
        self.calculate_performance_measures(distribution, states)

    def calculate_performance_measures(self, distribution: list, states: list) -> None:
        from analytical_calculations.logs import log_message

        for state, state_probability in enumerate(distribution):
            log_message(f'P[{pretty_state(states[state])}] = {state_probability}')
            self.calculate_avg_queue(states, state, state_probability)
            self.calculate_avg_free_servers(states, state, state_probability)
            self.calculate_avg_free_servers_if_queues_not_empty(states, state, state_probability)
            self.calculate_avg_demands_on_servers(states, state, state_probability)
            self.calculate_failure_probability(states, state, state_probability)

        p1 = self.params.lambda1 / self.params.total_lambda
        p2 = self.params.lambda2 / self.params.total_lambda
        # RANDOM demand arrives at the systems and get failed
        self.performance_measures.failure_probability = p1 * self.performance_measures.failure_probability1 + \
                                                        p2 * self.performance_measures.failure_probability2

        self.calculate_response_time()

    def calculate_response_time(self) -> None:
        effective_lambda1 = self.params.lambda1 * (1 - self.performance_measures.failure_probability1)
        effective_lambda2 = self.params.lambda2 * (1 - self.performance_measures.failure_probability2)

        queue_waiting1 = self.performance_measures.avg_queue1 / effective_lambda1
        queue_waiting2 = self.performance_measures.avg_queue2 / effective_lambda2

        self.calculate_response_time_solution1(queue_waiting1, queue_waiting2)
        # self.calculate_response_time_solution2(effective_lambda1, effective_lambda2)

        self.performance_measures.response_time = (self.performance_measures.avg_queue1 +
                                                   self.performance_measures.avg_queue2 +
                                                   self.performance_measures.avg_demands_on_servers1 +
                                                   self.performance_measures.avg_demands_on_servers2) / (
                                                          effective_lambda1 + effective_lambda2)

    def calculate_response_time_solution1(self, queue_waiting1: float, queue_waiting2: float) -> None:
        self.performance_measures.response_time1 = queue_waiting1 + harmonic_sum(
            self.params.fragments_numbers[0]) / self.params.mu
        self.performance_measures.response_time2 = queue_waiting2 + harmonic_sum(
            self.params.fragments_numbers[1]) / self.params.mu

    def calculate_response_time_solution2(self, effective_lambda1: float, effective_lambda2: float) -> None:
        self.performance_measures.response_time1 = (self.performance_measures.avg_queue1 +
                                                    self.performance_measures.avg_demands_on_servers1) / \
                                                   effective_lambda1
        self.performance_measures.response_time2 = (self.performance_measures.avg_queue2 +
                                                    self.performance_measures.avg_demands_on_servers2) / \
                                                   effective_lambda2

    def calculate_avg_queue(self, states: list, state: int, state_probability: float) -> None:
        self.performance_measures.avg_queue1 += states[state][0][0] * state_probability
        self.performance_measures.avg_queue2 += states[state][0][1] * state_probability

    def calculate_avg_free_servers(self, states: list, state: int, state_probability: float) -> None:
        self.performance_measures.avg_free_servers += \
            (self.params.servers_number -
             (len(states[state][1][0]) * self.params.fragments_numbers[0] +
              len(states[state][1][1]) * self.params.fragments_numbers[1])) * state_probability

    def calculate_avg_free_servers_if_queues_not_empty(self, states: list,
                                                       state: int, state_probability: float) -> None:
        if states[state][0][0] + states[state][0][1] != 0:
            self.performance_measures.avg_free_servers_if_queues_not_empty += \
                (self.params.servers_number -
                 (len(states[state][1][0]) * self.params.fragments_numbers[0] +
                  len(states[state][1][1]) * self.params.fragments_numbers[1])) * state_probability

    def calculate_avg_demands_on_servers(self, states: list, state: int, state_probability: float) -> None:
        self.performance_measures.avg_demands_on_servers1 += \
            (len(states[state][1][0]) * self.params.fragments_numbers[0] * state_probability) / \
            self.params.fragments_numbers[0]

        self.performance_measures.avg_demands_on_servers2 += \
            (len(states[state][1][1]) * self.params.fragments_numbers[1] * state_probability) / \
            self.params.fragments_numbers[1]

        self.performance_measures.avg_demands_on_servers += \
            ((len(states[state][1][0]) * self.params.fragments_numbers[0] +
              len(states[state][1][1]) * self.params.fragments_numbers[1]) * state_probability) / \
            (self.params.fragments_numbers[0] + self.params.fragments_numbers[1])

    def calculate_failure_probability(self, states: list, state: int, state_probability: float) -> None:
        if states[state][0][0] == self.params.queues_capacities[0]:
            self.performance_measures.failure_probability1 += state_probability

        if states[state][0][1] == self.params.queues_capacities[1]:
            self.performance_measures.failure_probability2 += state_probability

        if (states[state][0][0] == self.params.queues_capacities[0]) and \
                (states[state][0][1] == self.params.queues_capacities[1]):
            self.performance_measures.blocked_all_queues_probability += state_probability

    def get_norm_const(self) -> float:
        class1_probability = self.params.lambda1 / (self.params.lambda1 + self.params.lambda2)
        class2_probability = 1 - class1_probability
        queue_waiting_probability1 = class1_probability * (1 - self.performance_measures.failure_probability1)
        queue_waiting_probability2 = class2_probability * (1 - self.performance_measures.failure_probability2)
        return 1 / (queue_waiting_probability1 + queue_waiting_probability2)


def harmonic_sum(k: int) -> float:
    return sum(1 / i for i in range(1, k + 1))
