from model_properties.network_params import Params
from .demand import Demand
from .server import Server


class ServersWrapper:
    """This class contains auxiliary functions for working with servers."""

    def __init__(self, mu: float, servers_number: int) -> None:
        """
        @param mu: demand service rate
        @param servers_number: number of servicing servers
        """
        self.mu = mu
        self.servers = [Server(self.mu) for _ in range(servers_number)]

    def distribute_fragments(self, demand: Demand, current_time: float) -> None:
        """The function distributes a demand fragments by servers.

        @param demand: demand, fragments of which must be assigned to servers
        @param current_time: current simulation time of the model
        """
        count = 0
        # distributing fragments over the servers
        for server in self.servers:
            if server.is_free and count < demand.fragments_number:
                server.to_occupy(demand.fragments[count], current_time)
                count += 1
        if count != demand.fragments_number:
            raise Exception(
                "Incorrect number of fragments was distributed between servers"
            )

    def get_number_of_free_servers(self) -> int:
        """The function returns the number of free servers."""
        return len([True for server in self.servers if server.is_free])

    def get_min_end_service_time_for_demand(self) -> float:
        """The function returns the near term of the end of service of the claim."""
        service_duration_fragments = self.get_fragments_service_durations()
        # list of service times for all demands on servers at the moment
        max_service_duration = []

        for duration in service_duration_fragments:
            max_service_duration.append(max(duration))

        return min(max_service_duration)

    def get_fragments_service_durations(self) -> list:
        """The function returns a list of lists of each demand fragments servicing durations in the network."""
        demands_on_servers = self.get_demands_ids_on_servers()
        lists_of_fragments_service_durations = [
            [] for _ in range(len(demands_on_servers))
        ]

        for demand_id in demands_on_servers:
            for server in self.servers:
                if not server.is_free and server.fragment.parent_id == demand_id:
                    lists_of_fragments_service_durations[
                        demands_on_servers.index(demand_id)
                    ].append(server.end_service_time)

        return lists_of_fragments_service_durations

    def get_demands_ids_on_servers(self) -> list:
        """The function returns a list containing all demand ids on servers at the moment."""
        demands_ids_on_servers = set()

        for server in self.servers:
            if not server.is_free:
                demands_ids_on_servers.add(server.fragment.parent_id)

        return list(demands_ids_on_servers)

    def get_demand_id_with_min_end_service_time(self) -> int:
        """The function returns the demand id with the closest service completion time."""
        min_end_service_time = self.get_min_end_service_time_for_demand()
        for server in self.servers:
            if server.end_service_time == min_end_service_time:
                return server.fragment.parent_id

    def to_free_demand_fragments(self, demand_id: int) -> None:
        """The function frees servers from demand fragments leaving the system.

        @param demand_id: demand id which have to release servers
        """
        for server in self.servers:
            if (not server.is_free) and (server.fragment.parent_id == demand_id):
                server.to_free()

    def can_some_class_occupy(self, params: Params) -> bool:
        """
        Check if there is a class that can occupy servers
        """
        classes_number = len(params.fragments_numbers)
        for i in range(classes_number):
            if self.can_occupy(i, params):
                return True
        return False

    def can_any_class_to_occupy(self, params: Params) -> bool:
        classes_number = len(params.fragments_numbers)
        for i in range(classes_number):
            if not self.can_occupy(i, params):
                return False
        return True

    def can_occupy(self, class_id: int, params: Params) -> bool:
        """The function checks if the this class demand can service on the servers.

        @param params: network configuration parameters
        @param class_id: demand class
        """
        return self.get_number_of_free_servers() >= params.fragments_numbers[class_id]

    def check_if_possible_put_demand_on_servers(self, params: Params) -> bool:
        """The function checks if it is possible to put a demand on servers."""
        return bool(
            [
                True
                for class_id in range(len(params.fragments_numbers))
                if self.can_occupy(class_id, params)
            ]
        )

    def get_required_view_of_servers_state(self, current_time: float) -> tuple:
        # return view state: ((a1...an), (b1...bm))
        a, b = [], []
        checked_fragments = []

        for server in self.servers:
            if not server.is_free and not (
                server.fragment.parent_id in checked_fragments
            ):
                if server.fragment.class_id == 0:
                    a.append(
                        self._get_end_service_times_for_sibling_fragments(
                            server.fragment.parent_id, checked_fragments
                        )
                    )
                elif server.fragment.class_id == 1:
                    b.append(
                        self._get_end_service_times_for_sibling_fragments(
                            server.fragment.parent_id, checked_fragments
                        )
                    )
        for i in a:
            a[a.index(i)] = len([True for j in i if j >= current_time])

        for i in b:
            b[b.index(i)] = len([True for j in i if j >= current_time])

        return tuple(sorted(a)), tuple(sorted(b))

    def _get_end_service_times_for_sibling_fragments(
        self, fragment_parent_id: int, checked_fragments: list
    ) -> list:
        times = []
        checked_fragments.append(fragment_parent_id)
        for server in self.servers:
            if not server.is_free and server.fragment.parent_id == fragment_parent_id:
                times.append(server.end_service_time)
        return times
