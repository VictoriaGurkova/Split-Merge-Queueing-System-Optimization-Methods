import logging

empty_set_str = "\u2205"

logger = logging.getLogger()


def print_states(states: list, func) -> None:
    for state_id, state in enumerate(states):
        logger.debug(f"S({state_id}) = {func(state)}")


def pretty_servers_state(servers_state: list) -> str:
    elements = []
    for s in servers_state:
        if len(s) == 0:
            elements.append(empty_set_str)
        else:
            elements.append(str(s))
    return (
        "("
        + ", ".join(elements).replace("(", "{").replace(",)", "}").replace(")", "}")
        + ")"
    )


def pretty_state(state: [list, set]) -> str:
    queues_state = state[0]
    servers_state = state[1]
    return "(" + str(queues_state) + ": " + pretty_servers_state(servers_state) + ")"
