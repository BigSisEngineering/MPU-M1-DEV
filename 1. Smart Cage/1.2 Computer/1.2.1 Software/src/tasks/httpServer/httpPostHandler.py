# ------------------------------------------------------------------------------------------------ #
from src import BscbAPI
from src import data
from src.BscbAPI.BscbAPI import BScbAPI

from src.app import handler


POST_LIST = [
    "STAR_WHEEL",
    "STAR_WHEEL_INIT",
    "UNLOADER_INIT",
    "ENABLE_DUMMY",
    "ENABLE_PNP",
    "DISABLE_DUMMY",
    "DISABLE_PNP",
    "SET_STAR_WHEEL_SPEED",
    "SET_DUMMY_UNLOAD_PROBABILITY",
    "SET_PNP_CONFIDENCE_LEVEL",
    "CLEAR_STAR_WHEEL_ERROR",
    "CLEAR_UNLOADER_ERROR",
    "MOVE_CW",
    "MOVE_CCW",
    "UNLOAD",
]


def generateFuncName(arg):
    return f"post_{arg}"


def send_200_response(server):
    server.send_response(200)
    server.send_header("Cache-Control", "no-cache, private")
    server.send_header("Pragma", "no-cache")
    server.end_headers()


def post_STAR_WHEEL(server):
    with BScbAPI("/dev/ttyACM0", 115200) as board:
        # board.starWheelInit()
        for _ in range(3):
            board.starWheelMoveTime(server.parsed_url[2])
    send_200_response(server)


def post_STAR_WHEEL_INIT(server):
    send_200_response(server)
    if not data.dummy_enabled:
        server.wfile.write("star wheel init will be proceed".encode())
        handler.init_star_wheel()
    else:
        server.wfile.write("Error, disable dummy".encode())


def post_UNLOADER_INIT(server):
    send_200_response(server)
    if not data.dummy_enabled:
        server.wfile.write("unloader init will be proceed".encode())
        handler.init_unloader()
    else:
        server.wfile.write("Error, disable dummy".encode())


def post_ENABLE_PNP(server):
    send_200_response(server)
    # with data.lock_board_params:
    # if not data.unloader_inited or not data.star_wheel_inited or data.is_unloader_error or data.is_star_wheel_error:
    #     server.wfile.write("Error, pnp cannot enable".encode())
    # else:
    server.wfile.write("pnp Enabled".encode())
    with data.lock:
        data.pnp_enabled = True
    # handler.enable_pnp()


def post_ENABLE_DUMMY(server):
    send_200_response(server)
    # with data.lock_board_params:
    #     if not data.unloader_inited or not data.star_wheel_inited or data.is_unloader_error or data.is_star_wheel_error:
    #         server.wfile.write("Error, dummy cannot enable".encode())
    #     else:
    server.wfile.write("Dummy Enabled".encode())
    with data.lock:
        data.dummy_enabled = True
    # handler.enable_dummy()


def post_DISABLE_DUMMY(server):
    send_200_response(server)
    server.wfile.write("Dummy Disabled".encode())
    with data.lock:
        data.dummy_enabled = False
    # handler.enable_dummy()


def post_DISABLE_PNP(server):
    send_200_response(server)
    # with data.lock_board_params:
    # if not data.unloader_inited or not data.star_wheel_inited or data.is_unloader_error or data.is_star_wheel_error:
    #     server.wfile.write("Error, pnp cannot enable".encode())
    # else:
    server.wfile.write("pnp Disabled".encode())
    with data.lock:
        data.pnp_enabled = False
    # handler.enable_pnp()


def post_SET_STAR_WHEEL_SPEED(server):
    send_200_response(server)

    given_speed = int(server.parsed_url[2])
    if given_speed >= 600 and given_speed <= 5000:
        server.wfile.write(f"Speed set to {given_speed}".encode())
    else:
        server.wfile.write(f"speed should be 600-5000ms".encode())

    with data.lock:
        data.star_wheel_duration_ms = given_speed


def post_SET_DUMMY_UNLOAD_PROBABILITY(server):
    send_200_response(server)

    given_probability = int(server.parsed_url[2])
    if given_probability >= 0 and given_probability <= 100:
        server.wfile.write(f"Probability set to {given_probability}".encode())
    else:
        server.wfile.write(f"speed should be 0-100".encode())

    with data.lock:
        data.unload_probability = given_probability / 100


def post_SET_PNP_CONFIDENCE_LEVEL(server):
    send_200_response(server)

    given_confidence = int(server.parsed_url[2])
    if given_confidence >= 0 and given_confidence <= 100:
        server.wfile.write(f"Confidence set to {given_confidence}".encode())
    else:
        server.wfile.write(f"Confidence should be 0-100".encode())

    with data.lock:
        data.pnp_confidence = given_confidence / 100


def post_CLEAR_STAR_WHEEL_ERROR(server):
    send_200_response(server)
    server.wfile.write("post_CLEAR_STAR_WHEEL_ERROR".encode())
    handler.clear_star_wheel_error()


def post_CLEAR_UNLOADER_ERROR(server):
    send_200_response(server)
    server.wfile.write("CLEAR_UNLOADER_ERROR".encode())
    handler.clear_unloader_error()


def post_MOVE_CW(server):
    send_200_response(server)
    server.wfile.write("MOVE CW".encode())
    handler.move_star_wheel_cw()


def post_MOVE_CCW(server):
    send_200_response(server)
    server.wfile.write("MOVE CCW".encode())
    handler.move_star_wheel_ccw()


def post_CLEAR_UNLOADER_ERROR(server):
    send_200_response(server)
    server.wfile.write("CLEAR_UNLOADER_ERROR".encode())
    handler.clear_unloader_error()


def post_UNLOAD(server):
    send_200_response(server)
    server.wfile.write("UNLOAD".encode())
    handler.unload()
