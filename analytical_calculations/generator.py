from collections import defaultdict

import numpy as np
from scipy.linalg import expm

from handlers import arrival_handler, leaving_handler
from logs import log_message, log_state, log_state_config
from model_properties.network_params import Params
from states.states_functional import get_state_config
from policy.states_policy import Policy


def get_achievable_states(params: Params, states_policy: Policy, current_state: list) -> defaultdict:
    log_state(current_state)
    states_and_rates = defaultdict(float)

    state_config = get_state_config(params, current_state)
    log_state_config(state_config)

    arrival_handler(params, state_config, states_and_rates)
    leaving_handler(params, state_config, states_policy, states_and_rates)

    return states_and_rates


def create_generator(states: list, states_policy: Policy, params: Params) -> np.ndarray:
    n = len(states)
    generator = np.zeros((n, n))
    for i, current_state in enumerate(states):
        states_and_rates = get_achievable_states(params, states_policy, current_state)
        for state, rate in states_and_rates.items():
            j = states.index(state)
            generator[i, j] += rate

    for i, row in enumerate(generator):
        generator[i, i] = -sum(row)

    return generator


def get_stationary_distribution(states: list, states_policy: Policy, params: Params) -> list:
    generator = create_generator(states, states_policy, params)
    log_message(f'Q = {generator}')
    np.savetxt("output/generator/Q.txt", generator, fmt='%0.0f')
    return expm(generator * 100000000000)[0]
