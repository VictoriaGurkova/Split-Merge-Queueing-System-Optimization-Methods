from random import random

from model_properties.network_params import Params
from simulation_model.clock import Clock
from simulation_model.entities.demand import Demand
from simulation_model.entities.wrapper import ServersWrapper
from simulation_model.logs import (
    log_arrival,
    log_full_queue,
    log_service_start,
    log_leaving,
    log_network_state,
)
from simulation_model.network_statistics import Statistics
from simulation_model.progress_bar import ProgressBar


class SplitMergeSystem:
    def __init__(
        self,
        params: Params,
        progress_bar: ProgressBar = None,
        selection_policy=None,
        reward_policy=None,
    ):
        """

        @param params:
        @param progress_bar:
        @param selection_policy:
        """

        self._params = params
        self._progress_bar = progress_bar
        self._selection_policy = selection_policy
        self._simulation_time = None

        self._times = Clock()
        # set the arrival time of the first demand
        self._times.update_arrival_time(params.total_lambda)

        self._queues = [[] for _ in range(len(params.fragments_numbers))]
        self._servers = ServersWrapper(params.mu, params.servers_number)

        self._first_class_arrival_probability = params.lambda1 / params.total_lambda

        self._demands_in_network = []
        self._served_demands = []

        self._next_queue_id_for_selection_by_selection_policy = None
        self._there_was_a_choice_before_leaving = False

        self._statistics = Statistics(self._params.fragments_numbers)

        # r-learning parameters
        self.actions = [0, 1]
        self.n_actions = len(self.actions)
        self._state_before_leaving = None
        self._reward_policy = reward_policy

        # reward accumulated between states
        self._reward_for_current_period = 0
        self._total_reward = 0

    """This class describes the split-merge queuing system simulation model.

    Two classes of demand, two queues for demand.
    The progression of simulation time is from event to event.
    Events: arrival demand, start service demand and leaving demand.

    """

    def run(self, simulation_time: int = None) -> Statistics:
        """

        @param simulation_time: model simulation duration.
        """

        self.set_simulation_time(simulation_time)
        while self._times.current <= self._simulation_time:
            self.step(None)

        self._statistics.calculate_statistics(self._served_demands)
        return self._statistics

    def step(self, action=None):
        old_time = self._times.current
        old_state = self._get_current_state()

        self._times.current = min(
            self._times.arrival, self._times.service_start, self._times.leaving
        )
        time_in_state = self._times.current - old_time

        if self._progress_bar:
            self._progress_bar.update_progress(
                self._times.current, self._simulation_time
            )
        log_network_state(self._times, self._servers)

        if self._times.current == self._times.arrival:
            self._demand_arrival()
        elif self._times.current == self._times.service_start:
            self._demand_service_start(action)
        elif self._times.current == self._times.leaving:
            self._demand_leaving()
        else:
            raise Exception("Incorrect event time")

        new_state = self._get_current_state()

        reward = None
        if self._reward_policy:
            reward = self._reward_policy(old_state, new_state, time_in_state)
        return new_state, reward

    def _first_step(self):
        r = 0
        while not self._there_was_a_choice_before_leaving:
            _, reward = self.step()
            r += reward
        return reward

    def _big_step(self, action):
        r = 0
        if not self._there_was_a_choice_before_leaving:
            raise Exception("Incorrect state")
        _, reward = self.step(action)
        r += reward

        if self._there_was_a_choice_before_leaving:
            raise Exception("Incorrect state")

        while not self._there_was_a_choice_before_leaving:
            _, r = self.step()
            reward += r

        return self._state_before_leaving, reward

    def need_make_action_for_next_step(self):
        return self._there_was_a_choice_before_leaving

    def reset(self):
        self._times = Clock()
        self._times.update_arrival_time(self._params.total_lambda)
        self._queues = [[] for _ in range(len(self._params.fragments_numbers))]
        self._servers = ServersWrapper(self._params.mu, self._params.servers_number)
        self._demands_in_network = []
        self._served_demands = []
        self._next_queue_id_for_selection_by_selection_policy = None
        self._there_was_a_choice_before_leaving = False
        self._statistics = Statistics(self._params.fragments_numbers)
        self._progress_bar.reset()

        self._total_reward = 0
        self._reward_for_current_period = 0

        return self._get_current_state()

    def get_params(self) -> Params:
        return self._params

    def _queue_is_full(self, class_id):
        return len(self._queues[class_id]) >= self._params.queues_capacities[class_id]

    def _demand_arrival(self) -> None:
        """Event describing the arrival of a demand to the system."""

        class_id = self._define_arriving_demand_class()
        demand = Demand(
            self._times.current, class_id, self._params.fragments_numbers[class_id]
        )

        if not self._queue_is_full(class_id):
            self._times.service_start = self._times.current
            self._queues[class_id].append(demand)
            log_arrival(demand, self._times.current)
        else:
            log_full_queue(demand, self._times.current)

        self._times.update_arrival_time(self._params.total_lambda)

    def _demand_service_start(self, action=None) -> None:
        """Event describing the start of servicing a demand."""

        have_taken_at_least_one_demand = False
        while self._servers.can_some_class_occupy(self._params):
            class_id = None
            if action and not self._there_was_a_choice_before_leaving:
                raise Exception("Incorrect state")

            # here we try to use the policy or an external action if it is possible
            if self._there_was_a_choice_before_leaving:
                potential_class_id = (
                    action
                    if action is not None
                    else self._next_queue_id_for_selection_by_selection_policy
                )
                if potential_class_id is None:
                    raise Exception("Incorrect state")
                if (
                    self._servers.can_occupy(potential_class_id, self._params)
                    and self._queues[potential_class_id]
                ):
                    class_id = potential_class_id

            # here we try to find any demand to service from queues in this order [queue1, queue2, ...]
            if class_id is None:
                for i in range(len(self._params.fragments_numbers)):
                    if self._servers.can_occupy(i, self._params) and self._queues[i]:
                        class_id = i
                        break

            if class_id is not None:
                have_taken_at_least_one_demand = True
                demand = self._queues[class_id].pop(0)
                self._servers.distribute_fragments(demand, self._times.current)
                self._demands_in_network.append(demand)
                demand.service_start_time = self._times.current
                log_service_start(demand, self._times.current)
            else:
                break

        self._there_was_a_choice_before_leaving = False
        self._next_queue_id_for_selection_by_selection_policy = None
        self._state_before_leaving = None

        self._times.service_start = float("inf")

        #  update time for demand leaving if we have taken any new demand
        if have_taken_at_least_one_demand:
            self._times.leaving = self._servers.get_min_end_service_time_for_demand()

    def _demand_leaving(self) -> None:
        """Event describing a demand leaving the system."""

        self._state_before_leaving = self._get_current_state()
        all_queue_not_empty = self._queues[0] and self._queues[1]

        leaving_demand_id = self._servers.get_demand_id_with_min_end_service_time()
        self._servers.to_free_demand_fragments(leaving_demand_id)
        demand = None

        for d in self._demands_in_network:
            if d.id == leaving_demand_id:
                demand = d
                self._demands_in_network.remove(demand)
                break

        demand.leaving_time = self._times.current
        self._served_demands.append(demand)
        self._set_events_times()

        can_apply_policy = (
            all_queue_not_empty and self.can_any_class_to_occupy_servers()
        )
        if can_apply_policy:
            self._there_was_a_choice_before_leaving = True
            if self._selection_policy is not None:
                self._next_queue_id_for_selection_by_selection_policy = (
                    self._selection_policy(self._state_before_leaving)
                )
                # otherwise it means we have external actions
        else:
            self._next_queue_id_for_selection_by_selection_policy = None
            self._there_was_a_choice_before_leaving = False

        log_leaving(demand, self._times.current)

    def can_any_class_to_occupy_servers(self):
        return self._servers.can_any_class_to_occupy(self._params)

    def _set_events_times(self) -> None:
        if self._servers.check_if_possible_put_demand_on_servers(self._params):
            self._times.service_start = self._times.current
        if not self._servers.get_demands_ids_on_servers():
            self._times.leaving = float("inf")
        else:
            self._times.leaving = self._servers.get_min_end_service_time_for_demand()

    def _get_current_state(self) -> tuple:
        return (
            len(self._queues[0]),
            len(self._queues[1]),
        ), self._servers.get_required_view_of_servers_state(self._times.current)

    def set_simulation_time(self, time):
        if time is not None:
            self._simulation_time = time

    def end_simulation(self):
        return self._times.current >= self._simulation_time

    def _define_arriving_demand_class(self) -> int:
        return 0 if random() < self._first_class_arrival_probability else 1
