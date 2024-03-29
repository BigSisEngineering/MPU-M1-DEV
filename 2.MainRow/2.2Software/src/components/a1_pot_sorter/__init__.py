from src.comm.http_duet import HTTPDuet

# -------------------------------------------------------- #
from src._shared_variables import Duet

print_name = "A1"


class PotSorter(HTTPDuet):
    def __init__(self, duet: Duet = Duet.A1) -> None:
        self._duet_name = duet.name
        super().__init__(duet.value)

    @property
    def is_ready(self) -> bool:
        return self.is_connected

    def start(self):
        if self.is_ready and self.is_idle:
            self.run_macro("run.g")
            print("{:^10}-{:^15} Start.".format(print_name, self._duet_name))

    def stop(self):
        if self.is_ready and not self.is_idle:
            self.abort()
            print("{:^10}-{:^15} Stop.".format(print_name, self._duet_name))
