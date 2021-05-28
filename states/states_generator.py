import itertools

from analytical_calculations.logs import log_message
from model_properties.network_params import Params
from .pretty_states import print_states, pretty_servers_state, pretty_state


def get_all_states(params, do_logging=False):

    servers_states = get_all_possible_servers_states(params.x, params.y, params)
    if do_logging:
        log_message('Fragment states on servers (not including queues):')
        print_states(servers_states, pretty_servers_state)

    servers_states = get_all_possible_servers_states(params.x, params.y, params)
    states = get_all_state_with_queues(servers_states, params.queues_capacities, params)
    if do_logging:
        log_message('\nSystem states along with queues:')
        print_states(states, pretty_state)

    return states


def get_all_possible_servers_states(x: int, y: int, params: Params) -> list:
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
