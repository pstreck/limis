import http
import logging
import shutil
import socket

from pathlib import Path
from websocket import create_connection


def get_http_response(host: str, port: int, method: str, path: str):
    http_client = http.client.HTTPConnection(host, port)
    http_client.request(method, path)

    http_client_response = http_client.getresponse()

    status = http_client_response.status
    response = http_client_response.read().decode('utf-8')

    http_client.close()

    return status, response


def listening(port):
    test_socket = socket.socket()

    try:
        test_socket.connect(('localhost', port))
    except socket.error:
        return False
    finally:
        test_socket.close()

    return True


def remove_directory(path: Path):
    if path.exists():
        shutil.rmtree(str(path), ignore_errors=False)


def remove_logfile():
    logger = logging.getLogger()
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.flush()
        handler.close()

    log_file = Path().cwd() / 'limis.log'

    if log_file.exists():
        log_file.unlink()


def send_websocket_message_and_get_response(host: str, port: int, path: str, message: str):
    websocket = create_connection('ws://{}:{}/{}'.format(host, port, path))
    websocket.send(message)
    response = websocket.recv()
    websocket.close()

    return response


def string_in_file(filename: str, string: str):
    found = False

    with open(filename) as file:
        lines = file.readlines()

        if len(list(filter(lambda x: string in x, lines))) > 0:
            found = True

        file.close()

    return found
