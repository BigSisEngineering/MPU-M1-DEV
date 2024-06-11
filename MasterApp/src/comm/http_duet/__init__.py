import requests
import threading
from typing import Optional, Tuple, Any, Union, Callable

# -------------------------------------------------------- #
from src import CLI
from src.CLI import Level

print_name = "HTTPDuet"
hide_exception = True


class HTTPDuet:
    def __init__(self, duet_ip: str) -> None:
        self._duet_ip = duet_ip
        self._timeout = 5  # seconds

        # -------------------------------------------------------- #
        self._lock_request = threading.Lock()

    # -------------------------------------------------------- #
    def _task_handler(func: Callable, arg: Optional[Any] = None) -> None:
        if arg is not None:
            arg = (arg,) if not isinstance(arg, tuple) else arg
            threading.Thread(target=func, args=(*arg,)).start()
        else:
            threading.Thread(target=func).start()

    @property
    def is_connected(self) -> bool:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                requests.get(url=f"http://{self._duet_ip}/", timeout=self._timeout)
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "CONN", e),
                    )
            finally:
                self._lock_request.release()

        CLI.printline(
            Level.WARNING,
            "({:^10})-({:^8}) Request timeout!".format(print_name, "CONN"),
        )
        return False

    @property
    def is_idle(self) -> bool:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                status = requests.get(
                    url=f"http://{self._duet_ip}/rr_status?type=3",
                    timeout=self._timeout,
                ).json()

                if status["status"] == "I":
                    return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "IS_IDLE", e),
                    )
            finally:
                self._lock_request.release()

        CLI.printline(
            Level.WARNING,
            "({:^10})-({:^8}) Request timeout!".format(print_name, "IS_IDLE"),
        )
        return False

    def run_macro(self, macro_name: str, param: str = None) -> bool:
        with self._lock_request:
            try:
                requests.get(
                    url=f'http://{self._duet_ip}/rr_gcode?gcode=M98 P"0:/macros/{macro_name}" {param}',
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "RUN_MCR", e),
                    )
        return False

    def run_command(self, command_name: str) -> bool:
        with self._lock_request:
            try:
                requests.get(
                    url=f"http://{self._duet_ip}/rr_gcode?gcode={command_name}",
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "RUN_CMD", e),
                    )
        return False

    def read_global(self, *args: str) -> Optional[Union[Tuple, int]]:
        return_val = []
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                global_vars = requests.get(
                    url=f"http://{self._duet_ip}/rr_model?key=global",
                    timeout=self._timeout,
                ).json()["result"]

                if len(args) > 1:
                    for arg in args:
                        if arg in global_vars:
                            return_val.append(global_vars[arg])
                        else:
                            return_val.append(None)

                    return tuple(return_val)

                else:
                    return global_vars[args[0]]

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "READ_GLB", e),
                    )
                if len(args) > 1:
                    for arg in args:
                        return_val.append(None)
                    return tuple(return_val)
            finally:
                self._lock_request.release()

        CLI.printline(
            Level.WARNING,
            "({:^10})-({:^8}) Request timeout!".format(print_name, "READ_GLB"),
        )
        return None

    def set_global(self, var_name: str, value: int) -> bool:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                requests.get(
                    url=f"http://{self._duet_ip}/rr_gcode?gcode=set global.{var_name}={value}",
                    timeout=self._timeout,
                )
                return True

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "SET_GLB", e),
                    )
            finally:
                self._lock_request.release()

        CLI.printline(
            Level.WARNING,
            "({:^10})-({:^8}) Request timeout!".format(print_name, "SET_GLB"),
        )
        return False

    def read_object(self, obj_name: str) -> Optional[Any]:
        if self._lock_request.acquire(timeout=self._timeout):
            try:
                result = requests.get(
                    url=f"http://{self._duet_ip}/rr_model?key={obj_name}",
                    timeout=self._timeout,
                ).json()["result"]
                return result

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "READ_OBJ", e),
                    )
            finally:
                self._lock_request.release()

        CLI.printline(
            Level.WARNING,
            "({:^10})-({:^8}) Request timeout!".format(print_name, "READ_OBJ"),
        )
        return None

    def abort(self) -> None:
        with self._lock_request:
            try:
                requests.get(
                    f"http://{self._duet_ip}/rr_gcode?gcode=M112 M999",
                    timeout=self._timeout,
                )

            except Exception as e:
                if not hide_exception:
                    CLI.printline(
                        Level.ERROR,
                        "({:^10})-({:^8}) Exception -> {}".format(print_name, "ABORT", e),
                    )


# -------------------------------------------------------- #
def debug():
    obj = HTTPDuet("192.168.83.100")

    print(obj.abort())
