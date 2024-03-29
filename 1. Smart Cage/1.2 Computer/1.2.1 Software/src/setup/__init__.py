import os
import configparser
import socket

# ------------------------------------------------------------------------------------------------ #
from src.CLI import Level
from src import CLI

CAGE_ID: str = None
MASTER_HOSTNAME: str = None
MASTER_IP: str = None
MASTER_SERVER_PORT: str = None
SOFTWARE_VERSION: str = None
ROW_NUMBER = "V3.Beta"

config_parser = configparser.ConfigParser()
config_parser.read(
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "DEFAULT.ini",
    )
)


def get_cage_id(arg=None):
    # Apply default if no argument given
    id = socket.gethostname() if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Cage id sets to: {id}")
    return id


def get_master_hostname(arg=None):
    # Apply default if no argument given
    hostname = config_parser.get("ROW_MASTER", "HOSTNAME") if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Master Hostname is: {hostname}")
    return hostname


def get_master_ip(arg=None):
    ip = ""
    try:
        result = socket.getaddrinfo(arg, None)
        ip = result[0][4][0]
        CLI.printline(Level.INFO, f"(setup)-Master IP set: {ip}")
    except socket.gaierror:
        CLI.printline(Level.WARNING, f"(setup)-Master IP cannout found. Is master exist? ")
    return ip


def get_master_server_port(arg=None):
    port = config_parser.get("ROW_MASTER", "HTTP_SERVER_PORT") if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Master HTTP server port set: {port}")
    return port


def get_software_version(arg=None):
    version = config_parser.get("VERSION", "SOFTWARE") if arg is None else arg
    CLI.printline(Level.INFO, f"(setup)-Software version set: {version}")
    return version


CAGE_ID = get_cage_id()
MASTER_HOSTNAME = get_master_hostname()
MASTER_IP = get_master_ip(MASTER_HOSTNAME)
MASTER_SERVER_PORT = get_master_server_port()
SOFTWARE_VERSION = get_software_version()
