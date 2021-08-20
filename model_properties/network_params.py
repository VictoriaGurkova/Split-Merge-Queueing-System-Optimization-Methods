from dataclasses import dataclass


@dataclass
class Params:
    mu: float
    lambda1: float
    lambda2: float
    servers_number: int
    fragments_numbers: list
    queues_capacities: list

    @property
    def total_lambda(self) -> float:
        return self.lambda1 + self.lambda2

    @property
    def x(self) -> int:
        return self.servers_number // self.fragments_numbers[0]

    @property
    def y(self) -> int:
        return self.servers_number // self.fragments_numbers[1]
