"""
limis server

Application server based on the Tornado framework. Tornado provides base web server, routing and application
functionality. More information can be found at: `https://www.tornadoweb.org/en/stable/index.html
<https://www.tornadoweb.org/en/stable/index.html>`_.
"""
import asyncio
import logging
import signal

from typing import Any

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.routing import Router

from limis.core import settings
from limis.server import messages


class Server:
    """
    Application Server
    """
    def __init__(self, router: Router, port: int = None):
        """
        Initializes the Server class.

        :param router: Tornado router object containing the base routing definition for the application. This is
          most common a single Application instance, or a RuleRouter.
        :param port: The port number for the server to listen on, this defaults to the server['default_port'] setting.
        :raises ValueError: Error indicating the port specified in settings is not valid.
        """
        self.logger = logging.getLogger(__name__)

        self._running = False
        self.stop_server = False

        self.router = router

        try:
            self.port = int(settings.server['default_port'] if port is None else port)
        except ValueError:
            msg = messages.SERVER_INIT_SETTINGS_INVALID_PORT.format(settings.server['default_port'])

            self.logger.error(msg)
            raise ValueError(msg)

        self.server = HTTPServer(router)

    @property
    def running(self) -> bool:
        """
        Property to get the currently running status of the server.

        :return: running status
        """
        return self._running

    def _signal_handler(self, signal_number: int, frame: Any):
        """
        Sets the stop_server class instance variable to True.

        :param signal_number: Signal number
        :param frame: Frame
        """
        if signal_number == signal.SIGINT:
            self.stop_server = True

    def _started(self):
        """
        Sets the running status of the server after it has been started.
        """
        self._running = True
        self.logger.info(messages.SERVER_START_STARTED)

    def start(self):
        """
        Starts the server.
        """
        self.logger.info(messages.SERVER_START_STARTING.format(self.port))

        try:
            signal.signal(signal.SIGINT, self._signal_handler)
        except ValueError:
            pass

        self.logger.debug(messages.SERVER_START_DETAILS_PORT.format(self.port))

        try:
            asyncio.get_event_loop()
        except RuntimeError:
            asyncio.set_event_loop(asyncio.new_event_loop())

        self.server.listen(self.port)

        PeriodicCallback(self.stop, 100).start()
        IOLoop.current().add_callback(self._started)
        IOLoop.current().start()

        self.server.close_all_connections()
        IOLoop.current().close(all_fds=True)

        self._running = False

        self.logger.info(messages.SERVER_START_STOPPED)

    def stop(self):
        """
        Stops the currently running server if the stop_server flag is set to True.
        """
        if self.stop_server:
            IOLoop.current().stop()
            self.logger.info(messages.SERVER_STOP_STOPPING)
