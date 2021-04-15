from dataclasses import dataclass, field


@dataclass
class PerformanceMeasures:
    response_time: float = 0
    response_time1: float = 0
    response_time2: float = 0

    failure_probability: float = 0
    failure_probability1: float = 0
    failure_probability2: float = 0

    avg_queue1: float = 0
    avg_queue2: float = 0

    avg_demands_on_servers: float = 0
    avg_demands_on_servers1: float = 0
    avg_demands_on_servers2: float = 0

    avg_free_servers: float = 0
    avg_free_servers_if_queues_not_empty: float = 0

    def __str__(self):
        return f"response_time = {self.response_time} \n" \
               f"response_time1 = {self.response_time1} \n" \
               f"response_time2 = {self.response_time2} \n" \
               f"failure_prob = {self.failure_probability} \n" \
               f"failure_prob1 = {self.failure_probability1} \n" \
               f"failure_prob2 = {self.failure_probability2} \n" \
               f"avg_queue1 = {self.avg_queue1} \n" \
               f"avg_queue2 = {self.avg_queue2} \n" \
               f"avg_demands_on_servers: {self.avg_demands_on_servers}\n" \
               f"avg_demands_on_servers1: {self.avg_demands_on_servers1}\n" \
               f"avg_demands_on_servers2: {self.avg_demands_on_servers2}\n" \
               f"avg_free_servers: {self.avg_free_servers}\n" \
               f"avg_free_servers_if_queues_not_empty: {self.avg_free_servers_if_queues_not_empty}\n"


@dataclass
class PerformanceMeasuresStorage:
    strategies: list = field(default_factory=list)

    response_times: list = field(default_factory=list)
    response_times1: list = field(default_factory=list)
    response_times2: list = field(default_factory=list)

    failure_probabilities: list = field(default_factory=list)
    failure_probabilities1: list = field(default_factory=list)
    failure_probabilities2: list = field(default_factory=list)

    avgs_queue1: list = field(default_factory=list)
    avgs_queue2: list = field(default_factory=list)

    avgs_demands_on_servers: list = field(default_factory=list)
    avgs_demands_on_servers1: list = field(default_factory=list)
    avgs_demands_on_servers2: list = field(default_factory=list)

    avgs_free_servers: list = field(default_factory=list)
    avgs_free_servers_if_queues_not_empty: list = field(default_factory=list)

    def append(self, strategy: tuple, performance_measures: PerformanceMeasures) -> None:
        self.strategies.append(strategy)
        self.response_times.append(performance_measures.response_time)
        self.response_times1.append(performance_measures.response_time1)
        self.response_times2.append(performance_measures.response_time2)
        self.failure_probabilities.append(performance_measures.failure_probability)
        self.failure_probabilities1.append(performance_measures.failure_probability1)
        self.failure_probabilities2.append(performance_measures.failure_probability2)
        self.avgs_queue1.append(performance_measures.avg_queue1)
        self.avgs_queue2.append(performance_measures.avg_queue2)
        self.avgs_demands_on_servers.append(performance_measures.avg_demands_on_servers)
        self.avgs_demands_on_servers1.append(performance_measures.avg_demands_on_servers1)
        self.avgs_demands_on_servers2.append(performance_measures.avg_demands_on_servers2)
        self.avgs_free_servers.append(performance_measures.avg_free_servers)
        self.avgs_free_servers_if_queues_not_empty.append(performance_measures.avg_free_servers_if_queues_not_empty)

    def show_difference(self) -> None:
        self.__print_difference_details("rt", self.response_times)
        self.__print_difference_details("rt1", self.response_times1)
        self.__print_difference_details("rt2", self.response_times2)
        self.__print_difference_details("fp", self.failure_probabilities)
        self.__print_difference_details("fp1", self.failure_probabilities1)
        self.__print_difference_details("fp2", self.failure_probabilities2)
        self.__print_difference_details("avg_q1", self.avgs_queue1)
        self.__print_difference_details("avg_q2", self.avgs_queue2)
        self.__print_difference_details("avg_ds_on_serv", self.avgs_demands_on_servers)
        self.__print_difference_details("avg_ds_on_serv1", self.avgs_demands_on_servers1)
        self.__print_difference_details("avg_ds_on_serv2", self.avgs_demands_on_servers2)
        self.__print_difference_details("avg_free_serv", self.avgs_free_servers)
        self.__print_difference_details("avg_free_serv_if_q_not_empty", self.avgs_free_servers_if_queues_not_empty)

    def __print_difference_details(self, name: str, _list: list):
        min_value = min(_list)
        min_strategy = self.strategies[_list.index(min_value)]
        max_value = max(_list)
        max_strategy = self.strategies[_list.index(max_value)]

        print(f"{name}:\n"
              f"min value: {min_value} -> strategy: {min_strategy}\n"
              f"max value: {max_value} -> strategy: {max_strategy}\n"
              f"difference: {max_value - min_value}\n")

    def __str__(self) -> str:
        return f"strategies = {self.strategies} \n" \
               f"response_time = {[round(rt, 5) for rt in self.response_times]} \n" \
               f"response_time1 = {[round(rt1, 5) for rt1 in self.response_times1]} \n" \
               f"response_time2 = {[round(rt2, 5) for rt2 in self.response_times2]} \n" \
               f"failure_prob = {[round(fp, 5) for fp in self.failure_probabilities]} \n" \
               f"failure_prob1 = {[round(fp1, 5) for fp1 in self.failure_probabilities1]} \n" \
               f"failure_prob2 = {[round(fp2, 5) for fp2 in self.failure_probabilities2]} \n" \
               f"avg_queue1 = {[round(q1, 5) for q1 in self.avgs_queue1]} \n" \
               f"avg_queue2 = {[round(q2, 5) for q2 in self.avgs_queue2]} \n" \
               f"avg_demands_on_servers: {[round(d, 5) for d in self.avgs_demands_on_servers]}\n" \
               f"avg_demands_on_servers1: {[round(d1, 5) for d1 in self.avgs_demands_on_servers1]}\n" \
               f"avg_demands_on_servers2: {[round(d2, 5) for d2 in self.avgs_demands_on_servers2]}\n" \
               f"avg_free_servers: {[round(s, 5) for s in self.avgs_free_servers]}\n" \
               f"avg_free_servers_if_queues_not_empty: " \
               f"{[round(sq, 5) for sq in self.avgs_free_servers_if_queues_not_empty]}\n"
