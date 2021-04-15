import itertools

from model_properties.network_params import Params
from performance_measures import PerformanceMeasures
from states.pretty_states import print_states, pretty_servers_state, pretty_state


class Calculations:

    def __init__(self, params: Params) -> None:
        self.params = params
        self.performance_measures = PerformanceMeasures()

        self.x = params.servers_number // params.fragments_numbers[0]
        self.y = params.servers_number // params.fragments_numbers[1]

    def calculate(self, states_policy) -> None:
        from generator import get_stationary_distribution
        from logs import log_network_configuration, log_message

        log_network_configuration(self.params)
        states = self.get_all_states()

        distribution = get_stationary_distribution(states, states_policy, self.params)
        log_message(f'Stationary distribution P_i:\n {distribution}')
        log_message(f'Check sum P_i: {sum(distribution)}')
        self.calculate_performance_measures(distribution, states)

    def calculate_performance_measures(self, distribution: list, states: list) -> None:
        from logs import log_message

        for state, state_probability in enumerate(distribution):
            log_message(f'P[{pretty_state(states[state])}] = {state_probability}')
            self.calculate_avg_queue(states, state, state_probability)
            self.calculate_avg_free_servers(states, state, state_probability)
            self.calculate_avg_free_servers_if_queues_not_empty(states, state, state_probability)
            self.calculate_avg_demands_on_servers(states, state, state_probability)
            self.calculate_failure_probability(states, state, state_probability)

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

        if states[state][0][0] == self.params.queues_capacities[0] or \
                states[state][0][1] == self.params.queues_capacities[1]:
            self.performance_measures.failure_probability += state_probability

    def get_norm_const(self) -> float:
        class1_probability = self.params.lambda1 / (self.params.lambda1 + self.params.lambda2)
        class2_probability = 1 - class1_probability
        queue_waiting_probability1 = class1_probability * (1 - self.performance_measures.failure_probability1)
        queue_waiting_probability2 = class2_probability * (1 - self.performance_measures.failure_probability2)
        return 1 / (queue_waiting_probability1 + queue_waiting_probability2)

    def get_all_states(self, logs=False):
        from logs import log_message

        servers_states = get_servers_states(self.x, self.y, self.params)
        if logs:
            log_message('Fragment states on servers (not including queues):')
            print_states(servers_states, pretty_servers_state)

        servers_states = get_servers_states(self.x, self.y, self.params)
        states = get_all_state_with_queues(servers_states, self.params.queues_capacities, self.params)
        if logs:
            log_message('\nSystem states along with queues:')
            print_states(states, pretty_state)

        return states


def get_servers_states(x: int, y: int, params: Params) -> list:
    server_states = set()
    for i in range(x + 1):
        for j in range(y + 1):
            total_number_of_tasks = params.fragments_numbers[0] * i + \
                                    params.fragments_numbers[1] * j
            if params.servers_number < total_number_of_tasks:
                continue
            x_set = sorted(get_fragments_lots(i, params.fragments_numbers[0]))
            y_set = sorted(get_fragments_lots(j, params.fragments_numbers[1]))
            server_states.update(itertools.product(x_set, y_set))
    return list(server_states)


def get_all_state_with_queues(server_states: list, queues_capacities: list, params: Params) -> list:
    states = []
    queue_states = set(itertools.product(range(queues_capacities[0] + 1),
                                         range(queues_capacities[1] + 1)))

    for q_state in queue_states:
        for server_state in server_states:
            if check_possible_state(q_state, server_state, params):
                states.append((q_state, server_state))
    return states


def get_fragments_lots(demands_number: int, fragments_in_class: int) -> list:
    return list(itertools.combinations_with_replacement(
        range(1, fragments_in_class + 1), demands_number))


def check_possible_state(q_state: tuple, state: list, params: Params) -> bool:
    free_servers_number = \
        get_free_servers_number_for_server_state(params, state)
    if q_state[0] and free_servers_number >= params.fragments_numbers[0]:
        return False
    if q_state[1] and free_servers_number >= params.fragments_numbers[1]:
        return False
    return True


def get_free_servers_number_for_server_state(params: Params, server_state: list) -> int:
    number = params.servers_number - \
             (len(server_state[0]) * params.fragments_numbers[0] +
              len(server_state[1]) * params.fragments_numbers[1])
    if number < 0:
        raise Exception('Number of free servers for states < 0, '
                        'it is not correct state')
    return number


def harmonic_sum(k: int) -> float:
    return sum(1 / i for i in range(1, k + 1))
