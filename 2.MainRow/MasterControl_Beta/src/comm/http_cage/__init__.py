import requests
import json
import threading
import paramiko
import time
from typing import Optional, Dict

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "HTTPGate"

# -------------------------------------------------------- #
from src._shared_variables import SV

hide_exception = True

USERNAME = "linaro"
PASSWORD = "linaro"

status_default = {
    "sensors_values": "loading...",
    "star_wheel_status": "loading...",
    "unloader_status": "loading...",
    "mode": "loading...",
}


class HTTPCage:
    def __init__(self, hostname: str):
        self._gate_ip: Optional[str] = None
        self._hostname = hostname
        self._timeout = 2  # seconds

        # -------------------------------------------------------- #
        self._previous_pot_num = 0
        self._pot_num_thresh = 13
        self._lock_request = threading.Lock()

        # -------------------------------------------------------- #
        threading.Thread(target=self._find_ip_from_hostname).start()

    # PRIVATE
    # -------------------------------------------------------- #
    def _find_ip_from_hostname(self) -> None:

        with self._lock_request:
            CLI.printline(
                Level.INFO,
                "({:^10})-({:^8}) [{:^10}] -> Start".format(
                    print_name, "FIND IP", self._hostname
                ),
            )

            time_stamp = time.time()
            interval = 5  # seconds

            while not SV.KILLER_EVENT.is_set() and self._gate_ip is None:
                if (time.time() - time_stamp) > interval:
                    try:
                        # Create an SSH client
                        ssh_client = paramiko.SSHClient()
                        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                        # Connect to the remote device
                        ssh_client.connect(
                            self._hostname + ".local",
                            username=USERNAME,
                            password=PASSWORD,
                        )

                        # Run the 'ip addr show eth0' command to get information about the eth0 interface
                        stdin, stdout, stderr = ssh_client.exec_command(
                            "ip addr show eth0"
                        )

                        # Read the output and extract the IP address
                        output = stdout.read().decode()
                        lines = output.split("\n")
                        for line in lines:
                            if (
                                "inet " in line
                            ):  # Look for the line containing 'inet ' (IPv4 address)
                                ip_address = line.split()[1].split("/")[0]

                                CLI.printline(
                                    Level.INFO,
                                    "({:^10})-({:^8}) [{:^10}] -> {}".format(
                                        print_name,
                                        "FIND IP",
                                        self._hostname,
                                        ip_address,
                                    ),
                                )

                                self._gate_ip = ip_address

                                # Close the SSH connection
                                ssh_client.close()

                        ssh_client.close()

                    except Exception as e:
                        if not hide_exception:
                            CLI.printline(
                                Level.ERROR,
                                "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(
                                    print_name, "FIND IP", self._hostname, e
                                ),
                            )

                    if self._hostname is None:
                        CLI.printline(
                            Level.WARNING,
                            "({:^10})-({:^8}) IP for {} not found! Retrying in 5s...".format(
                                print_name, "FIND IP", self._hostname
                            ),
                        )
                        time_stamp = time.time()

        CLI.printline(
            Level.DEBUG,
            "({:^10})-({:^8}) [{:^10}] -> Stop".format(
                print_name, "FIND IP", self._hostname
            ),
        )

    # PUBLIC
    # -------------------------------------------------------- #
    @property
    def status(self) -> Dict:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                response = requests.get(
                    url=f"http://{self._gate_ip}:8080/BoardData",
                    timeout=self._timeout,
                )
                return json.loads(response.text)

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(
                            print_name, "GET STS", self._hostname, e
                        ),
                    )

            finally:
                self._lock_request.release()

        else:
            if not hide_exception:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(
                        print_name, "GET STS", self._hostname
                    ),
                )
        return status_default

    def execute_action(self, action_name: str) -> None:
        if action_name == "RESTART":
            return self.restart_software()
        else:
            try:
                requests.post(
                    url=f"http://{self._gate_ip}:8080/{action_name}",
                    timeout=1,
                )
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {}".format(
                        print_name, "EXEC", self._hostname, action_name
                    ),
                )
            except:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {} Failed!".format(
                        print_name, "EXEC", self._hostname, action_name
                    ),
                )

    def restart_software(self) -> None:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                ssh_client.connect(
                    self._gate_ip + ".local",
                    username=USERNAME,
                    password=PASSWORD,
                )

                stdin, stdout, stderr = ssh_client.exec_command("ip addr show eth0")

                output = stdout.read().decode()
                CLI.printline(
                    Level.INFO,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {}".format(
                        print_name, "EXEC", self._hostname, "RESTART SOFTWARE"
                    ),
                )

            except:
                CLI.printline(
                    Level.ERROR,
                    "({:^10})-({:^8}) [{:^10}] Execute -> {} Failed!".format(
                        print_name, "EXEC", self._hostname, "RESTART SOFTWARE"
                    ),
                )
            finally:
                self._lock_request.release()

    def fetch_pot_data(self) -> int:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                pot_num = requests.get(
                    url=f"http://{self._gate_ip}:8080/potData",
                    timeout=1,
                ).json()

                if isinstance(pot_num, int):
                    CLI.printline(
                        Level.DEBUG,
                        "({:^10})-({:^8}) [{:^10}] {:^3} pots.".format(
                            print_name, "POTDATA", self._hostname, pot_num
                        ),
                    )
                    self._previous_pot_num = pot_num
                    if (
                        pot_num > self._pot_num_thresh
                        and self._previous_pot_num > self._pot_num_thresh
                    ):
                        CLI.printline(
                            Level.WARNING,
                            "({:^10})-({:^8}) [{:^10}] Requested more than {} pots twice! Check infeed channel!".format(
                                print_name, "POTDATA", self._hostname, pot_num
                            ),
                        )
                        pot_num = 0

                    return pot_num

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) [{:^10}] Exception -> {}".format(
                            print_name, "POTDATA", self._hostname, e
                        ),
                    )

            finally:
                self._lock_request.release()

        else:
            if not hide_exception:
                CLI.printline(
                    Level.WARNING,
                    "({:^10})-({:^8}) [{:^10}] Failed to acquire request lock!".format(
                        print_name, "POTDATA", self._hostname
                    ),
                )
        return 0


# -------------------------------------------------------- #
def debug():
    try:
        gate12 = HTTPGate("m3gates12")
        gate34 = HTTPGate("m3gates34")
        gate56 = HTTPGate("m3gates56")

        time.sleep(10)

        print(gate12.status)
        print(gate34.status)
        print(gate56.status)

        print(gate12.set_mode("IDLE"))
        print(gate34.set_mode("IDLE"))
        print(gate56.set_mode("IDLE"))

        print(gate12.set_cycle_time(5000))
        print(gate34.set_cycle_time(5000))
        print(gate56.set_cycle_time(5000))

    except KeyboardInterrupt:
        SV.KILLER_EVENT.set()