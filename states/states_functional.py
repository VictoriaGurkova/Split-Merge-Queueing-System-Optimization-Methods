from dataclasses import dataclass

from analytical_calculations.logs import log_arrival_in_queue, log_arrival_on_servers
from model_properties.network_params import Params
from states.states_generator import get_free_servers_number_for_server_state


@dataclass
class StateConfig:
    capacity1: int
    capacity2: int
    q1: int
    q2: int
    servers: list
    free_servers_number: int

    def get_q_by_class_id(self, class_id: int) -> int:
        return self.q1 if class_id == 1 else self.q2

    def get_capacity_by_class_id(self, class_id: int) -> int:
        return self.capacity1 if class_id == 1 else self.capacity2


@dataclass
class UpdateState:
    servers_state_class1: list
    servers_state_class2: list
    q1: int
    q2: int
    free_servers_number: int

    def get_q_by_class_id(self, class_id: int) -> int:
        return self.q1 if class_id == 1 else self.q2

    def update_q_by_class_id(self, class_id: int) -> None:
        if class_id == 1:
            self.q1 -= 1
        else:
            self.q2 -= 1

    def get_servers_state_by_class_id(self, class_id: int) -> list:
        return self.servers_state_class1 if class_id == 1 else self.servers_state_class2

    def update_servers_state_by_class_id(self, class_id: int, value: list) -> None:
        if class_id == 1:
            self.servers_state_class1 += value
        else:
            self.servers_state_class2 += value

    def server_state_by_class_id_pop(self, class_id, index):
        if class_id == 1:
            self.servers_state_class1.pop(index)
        else:
            self.servers_state_class2.pop(index)

    def get_tuple_view(self) -> tuple:
        return (self.q1, self.q2), (
            tuple(sorted(self.servers_state_class1)),
            tuple(sorted(self.servers_state_class2)),
        )


def define_queue_state(
    q1: int,
    q2: int,
    servers: list,
    lambda1: float,
    lambda2: float,
    states_and_rates: dict,
    class_id: int,
) -> None:
    if class_id == 1:
        update_queue_state(q1 + 1, q2, servers, lambda1, states_and_rates, class_id)
    else:
        update_queue_state(q1, q2 + 1, servers, lambda2, states_and_rates, class_id)


def update_queue_state(
    q1: int,
    q2: int,
    servers: list,
    lambda_: float,
    states_and_rates: dict,
    class_id: int,
) -> None:
    state = create_state(q1, q2, servers[0], servers[1])
    log_arrival_in_queue(lambda_, state, class_id)
    states_and_rates[state] += lambda_


def define_servers_state(
    q1: int,
    q2: int,
    servers: list,
    lambda1: float,
    lambda2: float,
    states_and_rates: dict,
    params: Params,
    class_id: int,
) -> None:
    if class_id == 1:
        update_servers_state(
            q1, q2, servers, lambda1, states_and_rates, params, class_id
        )
    else:
        update_servers_state(
            q1, q2, servers, lambda2, states_and_rates, params, class_id
        )


def update_servers_state(
    q1: int,
    q2: int,
    servers: list,
    rate: float,
    states_and_rates: dict,
    params: Params,
    class_id: int,
) -> None:
    update_state = servers[class_id - 1]
    update_state += (params.fragments_numbers[class_id - 1],)

    state = (
        create_state(q1, q2, update_state, servers[1])
        if class_id == 1
        else create_state(q1, q2, servers[0], update_state)
    )

    log_arrival_on_servers(rate, state, class_id)
    states_and_rates[state] += rate


def update_system_state(
    state_config: StateConfig,
    update_state: UpdateState,
    params: Params,
    class_id: int,
    id: int,
) -> None:
    if state_config.get_q_by_class_id(id):
        while update_state.free_servers_number + params.fragments_numbers[
            class_id - 1
        ] >= params.fragments_numbers[id - 1] and update_state.get_q_by_class_id(id):
            update_state.update_servers_state_by_class_id(
                id, [params.fragments_numbers[id - 1]]
            )
            update_state.update_q_by_class_id(id)
            update_state.free_servers_number -= params.fragments_numbers[id - 1]


def create_state(q1: int, q2: int, first_class: list, second_class: list) -> tuple:
    return (q1, q2), (tuple(sorted(first_class)), tuple(sorted(second_class)))


def get_state_config(params: Params, current_state: list) -> StateConfig:
    state_config = StateConfig(
        capacity1=params.queues_capacities[0],
        capacity2=params.queues_capacities[1],
        q1=current_state[0][0],
        q2=current_state[0][1],
        servers=current_state[1],
        free_servers_number=get_free_servers_number_for_server_state(
            params, current_state[1]
        ),
    )
    return state_config


def get_updated_state(state_config: StateConfig) -> UpdateState:
    update_state = UpdateState(
        servers_state_class1=list(state_config.servers[0]),
        servers_state_class2=list(state_config.servers[1]),
        q1=state_config.q1,
        q2=state_config.q2,
        free_servers_number=state_config.free_servers_number,
    )
    return update_state


def have_a_choice(state: tuple, class_id: int, params: Params) -> bool:
    return get_free_servers_after_leaving(state[1], class_id, params) >= max(
        params.fragments_numbers
    )


def get_free_servers_after_leaving(
    server_state: tuple, class_id: int, params: Params
) -> int:
    return (
        params.servers_number
        - (
            len(server_state[0]) * params.fragments_numbers[0]
            + len(server_state[1]) * params.fragments_numbers[1]
        )
        + params.fragments_numbers[class_id]
    )
