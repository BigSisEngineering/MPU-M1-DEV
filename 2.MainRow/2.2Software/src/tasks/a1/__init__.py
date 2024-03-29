import threading
import time

# -------------------------------------------------------- #
from src import components

# -------------------------------------------------------- #
from src._shared_variables import SV

print_name = "POT_SORTER"


class A1:
    def __init__(self):
        # -------------------------------------------------------- #
        self.loop_thread = threading.Thread(target=self._loop)

    def _loop(self):
        time_stamp = time.time() - 300  # set to 5 mins ago for instant 1st pulse
        while not SV.KILLER_EVENT.is_set():
            if time.time() - time_stamp > SV.WATCHDOG:
                components.A1.start() if SV.run else components.A1.stop()

                time_stamp = time.time()

    # -------------------------------------------------------- #
    def start(self):
        self.loop_thread.start()
