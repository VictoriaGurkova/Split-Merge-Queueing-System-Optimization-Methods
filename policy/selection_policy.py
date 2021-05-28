import random

from model_properties.network_params import Params
from policy.states_policy import Policy


class DefaultSelectionPolicy:

    @staticmethod
    def direct_order(state: tuple) -> int:
        return 0

    @staticmethod
    def reverse_order(state: tuple) -> int:
        return 1

    @staticmethod
    def random_order(state: tuple) -> int:
        return random.randint(0, 1)
