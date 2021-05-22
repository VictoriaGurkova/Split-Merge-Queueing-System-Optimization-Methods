from random import random

from model_properties.network_params import Params
from simulation_model.clock import Clock
from simulation_model.entities.demand import Demand
from simulation_model.entities.wrapper import ServersWrapper
from simulation_model.logs import log_arrival, log_full_queue, log_service_start, log_leaving, log_network_state
from simulation_model.network_statistics import Statistics
from simulation_model.progress_bar import ProgressBar


class SplitMergeSystem:
    """This class describes the split-merge queuing system simulation model.

    Two classes of demand, two queues for demand.
    The progression of simulation time is from event to event.
    Events: arrival demand, start service demand and leaving demand.

    """

    def __init__(self,
                 params: Params,
                 progress_bar: ProgressBar,
                 selection_policy=None,
                 simulation_time=None):
        """

        @param params:
        @param progress_bar:
        @param selection_policy:
        """

        self._params = params
        self._progress_bar = progress_bar
        self._selection_policy = selection_policy
        self._simulation_time = 10_000 if simulation_time is None else simulation_time

        self._times = Clock()
        # set the arrival time of the first demand
        self._times.update_arrival_time(params.total_lambda)

        self._queues = [[] for _ in range(len(params.fragments_numbers))]
        self._servers = ServersWrapper(params.mu, params.servers_number)

        self._first_class_arrival_probability = params.lambda1 / params.total_lambda

        self._demands_in_network = []
        self._served_demands = []

        self._queue_id_for_selection = None
        self._there_is_a_choice = False

        self._statistics = Statistics(self._params.fragments_numbers)

        self.actions = [0, 1]
        self.n_actions = len(self.actions)

    def run(self, simulation_time: int = None) -> Statistics:
        """

        @param simulation_time: model simulation duration.
        """

        self.set_simulation_time(simulation_time)
        while self._times.current <= self._simulation_time:
            self.step()

        self._statistics.calculate_statistics(self._served_demands)
        return self._statistics

    def step(self, action=None):
        self._times.current = min(self._times.arrival, self._times.service_start, self._times.leaving)
        self._progress_bar.update_progress(self._times.current, self._simulation_time)
        log_network_state(self._times, self._servers)

        old_state = self._get_current_state()
        if self._times.current == self._times.arrival:
            self._demand_arrival()
            new_state = self._get_current_state()
            reward = self._get_reward_for_states(old_state, new_state)
            return new_state, reward, self.end_simulation()
        if self._times.current == self._times.service_start:
            self._demand_service_start(action)
            new_state = self._get_current_state()
            reward = self._get_reward_for_states(old_state, new_state)
            return new_state, reward, self.end_simulation()
        if self._times.current == self._times.leaving:
            self._demand_leaving()
            new_state = self._get_current_state()
            reward = self._get_reward_for_states(old_state, new_state)
            return new_state, reward, self.end_simulation()

    def reset(self):
        self._times = Clock()
        self._times.update_arrival_time(self._params.total_lambda)
        self._queues = [[] for _ in range(len(self._params.fragments_numbers))]
        self._servers = ServersWrapper(self._params.mu, self._params.servers_number)
        self._demands_in_network = []
        self._served_demands = []
        self._queue_id_for_selection = None
        self._there_is_a_choice = False
        self._statistics = Statistics(self._params.fragments_numbers)
        self._progress_bar.reset()

        return self._get_current_state()

    def get_params(self) -> Params:
        return self._params

    def _demand_arrival(self) -> None:
        """Event describing the arrival of a demand to the system."""

        class_id = self._define_arriving_demand_class(self._first_class_arrival_probability)
        demand = Demand(self._times.arrival,
                        class_id, self._params.fragments_numbers[class_id])

        if len(self._queues[class_id]) < self._params.queues_capacities[class_id]:
            self._times.service_start = self._times.current
            self._queues[class_id].append(demand)
            log_arrival(demand, self._times.current)
        else:
            log_full_queue(demand, self._times.current)

        self._times.update_arrival_time(self._params.total_lambda)

    def _demand_service_start(self, action=None) -> None:
        """Event describing the start of servicing a demand."""

        while self._servers.can_some_class_occupy(self._params):
            class_id = None

            if self._there_is_a_choice:
                class_id = self._queue_id_for_selection

            if class_id is None:
                for i in range(len(self._params.fragments_numbers)):
                    if self._servers.can_occupy(i, self._params) and self._queues[i]:
                        class_id = i
                        break

            if action is not None:
                class_id = action

            if class_id is not None:
                demand = self._queues[class_id].pop(0)
                self._servers.distribute_fragments(demand, self._times.current)
                self._demands_in_network.append(demand)
                demand.service_start_time = self._times.current
                log_service_start(demand, self._times.current)
            else:
                break

        self._times.service_start = float('inf')

        demand_exists = bool(self._servers.get_demands_ids_on_servers())
        if demand_exists:
            self._times.leaving = self._servers.get_min_end_service_time_for_demand()

    def _demand_leaving(self) -> None:
        """Event describing a demand leaving the system."""

        state = self._get_current_state()
        all_queue_not_empty = state[0][0] and state[0][1]

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

        can_apply_policy = all_queue_not_empty and self.can_any_class_to_occupy_servers()
        if self._selection_policy is not None:
            self._queue_id_for_selection = self._selection_policy(state) if can_apply_policy else None
            self._there_is_a_choice = True if can_apply_policy else False

        log_leaving(demand, self._times.current)

    def can_any_class_to_occupy_servers(self):
        return self._servers.can_any_class_to_occupy(self._params)

    def _set_events_times(self) -> None:
        if self._servers.check_if_possible_put_demand_on_servers(self._params):
            self._times.service_start = self._times.current
        if not self._servers.get_demands_ids_on_servers():
            self._times.leaving = float('inf')
        else:
            self._times.leaving = self._servers.get_min_end_service_time_for_demand()

    def _get_current_state(self) -> tuple:
        return (len(self._queues[0]), len(self._queues[1])), \
               self._servers.get_required_view_of_servers_state(self._times.current)

    def _get_reward_for_states(self, old_state, new_state):
        old = sum(old_state[1][0]) + sum(old_state[1][1])
        new = sum(new_state[1][0]) + sum(new_state[1][1])
        free_servers_num = self._params.servers_number - (len(new_state[1][0]) + len(new_state[1][0]))
        return -new - old - free_servers_num

    def set_simulation_time(self, time):
        if time is not None:
            self._simulation_time = time

    def end_simulation(self):
        return self._times.current >= self._simulation_time

    @staticmethod
    def _define_arriving_demand_class(probability: float) -> int:
        return 0 if random() < probability else 1
