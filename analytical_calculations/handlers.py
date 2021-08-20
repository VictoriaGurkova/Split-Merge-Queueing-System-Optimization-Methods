from collections import defaultdict

from analytical_calculations.logs import (
    log_event,
    log_lost_demand,
    log_leaving_demand,
    log_leaving_fragment,
)
from model_properties.network_params import Params
from policy.states_policy import Policy
from states.states_functional import (
    define_queue_state,
    define_servers_state,
    get_updated_state,
    update_system_state,
    create_state,
    StateConfig,
    have_a_choice,
)


def arrival_handler(
    params: Params, state_config: StateConfig, states_and_rates: defaultdict
) -> None:
    log_event("ARRIVAL")
    _arrival_handler_for_class(params, state_config, states_and_rates, class_id=1)
    _arrival_handler_for_class(params, state_config, states_and_rates, class_id=2)


def leaving_handler(
    params: Params,
    state_config: StateConfig,
    states_policy: Policy,
    states_and_rates: defaultdict,
) -> None:
    log_event("LEAVING")
    _leaving_handler_for_class(
        params, state_config, states_policy, states_and_rates, class_id=1
    )
    _leaving_handler_for_class(
        params, state_config, states_policy, states_and_rates, class_id=2
    )


def _arrival_handler_for_class(
    params: Params,
    state_config: StateConfig,
    states_and_rates: defaultdict,
    class_id: int,
) -> None:
    if state_config.get_q_by_class_id(
        class_id
    ) != state_config.get_capacity_by_class_id(class_id):
        if state_config.free_servers_number < params.fragments_numbers[class_id - 1]:
            define_queue_state(
                state_config.q1,
                state_config.q2,
                [state_config.servers[0], state_config.servers[1]],
                params.lambda1,
                params.lambda2,
                states_and_rates,
                class_id,
            )
        else:
            define_servers_state(
                state_config.q1,
                state_config.q2,
                [state_config.servers[0], state_config.servers[1]],
                params.lambda1,
                params.lambda2,
                states_and_rates,
                params,
                class_id,
            )
    else:
        log_lost_demand()


def _leaving_handler_for_class(
    params: Params,
    state_config: StateConfig,
    states_policy: Policy,
    states_and_rates: defaultdict,
    class_id: int,
) -> None:
    for index, unserved_fragments_number in enumerate(
        state_config.servers[class_id - 1]
    ):
        updated_state = get_updated_state(state_config)
        if unserved_fragments_number == 1:
            state = updated_state.get_tuple_view()
            if state in states_policy.states_with_policy and have_a_choice(
                state, class_id - 1, params
            ):
                # we get the number of the queue from which we take demand, according to the policy_vector
                queue_id = states_policy.policy_vector[
                    states_policy.states_with_policy.index(state)
                ]
                new_state = states_policy.adjacent_states[state][queue_id]
                log_leaving_demand(params.mu, new_state, class_id)
                states_and_rates[new_state] += params.mu
            else:
                updated_state.server_state_by_class_id_pop(class_id, index)
                update_system_state(state_config, updated_state, params, class_id, id=1)
                update_system_state(state_config, updated_state, params, class_id, id=2)
                new_state = create_state(
                    updated_state.q1,
                    updated_state.q2,
                    updated_state.servers_state_class1,
                    updated_state.servers_state_class2,
                )
                log_leaving_demand(params.mu, new_state, class_id)
                states_and_rates[new_state] += params.mu
        else:
            leave_rate = params.mu * unserved_fragments_number
            if class_id == 1:
                updated_state.servers_state_class1[index] -= 1
            else:
                updated_state.servers_state_class2[index] -= 1
            new_state = create_state(
                state_config.q1,
                state_config.q2,
                updated_state.servers_state_class1,
                updated_state.servers_state_class2,
            )
            log_leaving_fragment(leave_rate, new_state, class_id)
            states_and_rates[new_state] += leave_rate
