import time

from threading import Thread
from tornado.routing import Router
from unittest import TestCase

from limis.server import Server


class LimisServerTestCase(TestCase):
    http_port = 8080
    websocket_port = 8888

    @staticmethod
    def __run_http_server(router: Router, port: int):
        global http_server

        http_server = Server(router, port=port)
        http_server.logger.disabled = True
        http_server.start()

    @staticmethod
    def __run_websocket_server(router: Router, port: int):
        global websocket_server

        websocket_server = Server(router, port=port)
        websocket_server.logger.disabled = True
        websocket_server.start()

    @staticmethod
    def run_server(http_router: Router = None, http_port: int = None,
                   websocket_router: Router = None, websocket_port: int = None):

        if http_router:
            if not http_port:
                http_port = LimisServerTestCase.http_port

            thread = Thread(target=LimisServerTestCase.__run_http_server,
                            kwargs={'router': http_router, 'port': http_port})
            thread.daemon = True
            thread.start()

            time.sleep(1)

        if websocket_router:
            if not websocket_port:
                websocket_port = LimisServerTestCase.websocket_port

            thread = Thread(target=LimisServerTestCase.__run_websocket_server,
                            kwargs={'router': websocket_router, 'port': websocket_port})
            thread.daemon = True
            thread.start()

            time.sleep(1)

    def tearDown(self):
        try:
            if http_server.running:
                http_server.stop_server = True

                while http_server.running:
                    time.sleep(1)

            if websocket_server.running:
                websocket_server.stop_server = True

                while websocket_server.running:
                    time.sleep(1)
        except NameError:
            pass
