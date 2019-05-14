"""
limis management - commands

Individual command definition for management command line tool.
"""
import getopt
import signal
import time

from abc import ABC, abstractmethod
from pathlib import Path
from shutil import copytree, move
from threading import Thread
from typing import Any, List

from tornado.routing import RuleRouter

from limis.core import settings
from limis.core.utilities import get_root_services, get_version, initialize_logging, replace_template_strings
from limis.management import exit_codes, messages
from limis.server import Server as LimisServer
from limis.services.router import ServicesRouter


class Command(ABC):
    """
    Command

    Abstract class that defines a command.

    :attribute help: Command help text.
    :attribute help_arguments: Command arguments help text.
    :attribute name: Command name argument.
    """
    help = None
    help_arguments = None
    name = None

    @classmethod
    def invalid_arguments(cls) -> int:
        """
        Displays the invalid arguments message and arguments help text. Called when a command has been called with an
        invalid set of arguments.

        :return: Command line exit code, default INVALID_ARGUMENTS.
        """
        print(messages.COMMAND_LINE_INTERFACE_RUN_INVALID_ARGUMENTS)
        print(cls.help_arguments)

        return exit_codes.INVALID_ARGUMENTS

    @abstractmethod
    def run(self, args: List[str]) -> int:
        """
        Abstract method to execute the command logic.

        :param args: List of arguments passed to the command.
        :return: Exit code.
        """


class CreateProject(Command):
    """
    CreateProject

    Creates a new limis project.
    """
    help = 'Creates a limis project'
    help_arguments = '<project_name> [project_directory]'
    name = 'create_project'

    def run(self, args: List[str]) -> int:
        """
        Executes the create_project command. This command creates a new limis project based on the project template that
        is stored in limis.resources.project_template. If the directory is not passed with the arguments the current
        working directory is used as the parent and new directory with the project name will be created.

        :param args: Arguments should be a list with the project name and optionally the project directory.
        :return: Command line exit code.
        """
        if len(args) < 1 or len(args) > 2:
            return self.invalid_arguments()

        name = args[0]
        directory = None

        if len(args) == 2:
            directory = args[1]

        print(messages.COMMAND_CREATE_PROJECT_RUN_STARTED.format(name))

        if not directory:
            directory = Path.cwd() / name
        else:
            directory = Path(directory)

        project_template_directory = Path(__file__).parent.parent / Path('resources/project_template')

        try:
            copytree(str(project_template_directory), str(directory))
            move(str(directory / 'project'), str(directory / name))
        except OSError as error:
            print(messages.COMMAND_CREATE_PROJECT_RUN_ERROR.format(str(directory), str(error)))
            return exit_codes.ERROR_CREATING_PROJECT

        replace_template_strings(directory, ['name'], [name])

        print(messages.COMMAND_CREATE_PROJECT_RUN_COMPLETED.format(name))

        return exit_codes.SUCCESS


class CreateService(Command):
    """
    CreateService

    Creates a new limis service in the current project.
    """
    help = 'Create a limis service'
    help_arguments = 'service_name [path]'
    name = 'create_service'

    def run(self, args: List[str]) -> int:
        """
        Executes the create_service command. This command creates a new limis service based on the service template that
        is stored in limis.resources.service_template. If the path is not passed with the arguments the service name
        is used as the default path.

        :param args: Arguments should be a list with the service name and an optional path
        :return: Command line exit code
        """
        if len(args) < 1 or len(args) > 2:
            return self.invalid_arguments()

        name = args[0]

        if len(args) == 2:
            path = args[1]
        else:
            path = name

        print(messages.COMMAND_CREATE_SERVICE_RUN_STARTED.format(name))

        directory = Path.cwd() / path

        service_template_directory = Path(__file__).parent.parent / Path('resources/service_template')

        try:
            copytree(str(service_template_directory), str(directory))
        except OSError as error:
            print(messages.COMMAND_CREATE_SERVICE_RUN_ERROR.format(str(directory), str(error)))
            return exit_codes.ERROR_CREATING_SERVICE

        replace_template_strings(directory, ['name', 'path'], [name, name])

        print(messages.COMMAND_CREATE_SERVICE_RUN_COMPLETED.format(name))

        return exit_codes.SUCCESS


class Server(Command):
    """
    Server

    Command to start the limis server.
    """
    help = 'Starts the limis server'
    help_arguments = '-d, --debug\t\t\t\tsets debug mode on\n' \
                     '-p, --http\t\t\t\truns http server\n' \
                     '--http_port=PORT\t\tsets http server port\n' \
                     '-w, --websocket\t\t\truns websocket server\n' \
                     '--websocket_port=PORT\tsets websocket port\n'
    name = 'server'

    def __init__(self):
        """
        Initializes the Server command
        """
        self.debug = False
        self.http = False
        self.http_port = settings.server['default_http_port']
        self.websocket = False
        self.websocket_port = settings.server['default_websocket_port']

    @staticmethod
    def _run_http_server(router: RuleRouter, port: int):
        """
        Thread target to run the http server

        :param router:  Tornado RuleRouter
        :param port: Port to listen on
        """
        global http_server

        http_server = LimisServer(router, port=port)
        http_server.start()

    @staticmethod
    def _run_websocket_server(router: RuleRouter, port: int):
        """
        Thread target to run the websocket server

        :param router:  Tornado RuleRouter
        :param port: Port to listen on
        """
        global websocket_server

        websocket_server = LimisServer(router, port=port)
        websocket_server.start()

    @staticmethod
    def _http_server_running() -> bool:
        """
        Checks to see if the http server is running

        :return running: Boolean
        """
        try:
            running = http_server.running
        except NameError:
            running = False

        return running

    @staticmethod
    def _websocket_server_running() -> bool:
        """
        Checks to see if the websocket server is running

        :return running: Boolean
        """
        try:
            running = websocket_server.running
        except NameError:
            running = False

        return running

    @staticmethod
    def _signal_handler(signal_number: int, frame: Any):
        """
        Sets the stop_server class instance variable to True.

        :param signal_number: Signal number
        :param frame: Frame
        """
        if signal_number == signal.SIGINT:
            try:
                http_server.stop_server = True
            except NameError:
                pass

            try:
                websocket_server.stop_server = True
            except NameError:
                pass

    def parse_arguments(self, args: List[str]):
        """
        Parses arguments passed to the "server" command".

        Valid arguments;

            * -d / --debug: Enables debugging mode
            * -p / --http: Enables the HTTP server
            * --http_port=: Sets the HTTP server port, defaults to setting server['default_http_port']
            * -w / --websocket: Enables the WebSocket Server
            * --websocket_port=: Sets the WebSocket server port, defaults to setting server['default_http_port']

        :param args: List of arguments.
        :raises ValueError: Error indicating an invalid argument was passed in the args list.
        """
        if len(args) > 0:
            try:
                opts, args = getopt.getopt(args, 'dpw', ['debug', 'http', 'http_port=', 'websocket', 'websocket_port='])
            except getopt.GetoptError:
                print(messages.COMMAND_INVALID_ARGUMENT)
                raise ValueError(messages.COMMAND_INVALID_ARGUMENT)

            for opt, arg in opts:
                if opt in ['-d', '--debug']:
                    self.debug = True
                elif opt in ['-p', '--http']:
                    self.http = True
                elif opt == '--http_port':
                    try:
                        self.http_port = int(arg)
                    except ValueError:
                        msg = messages.COMMAND_SERVER_INVALID_PORT.format(arg)

                        print(msg)
                        raise ValueError(msg)
                elif opt in ['-w', '--websocket']:
                    self.websocket = True
                elif opt == '--websocket_port':
                    try:
                        self.websocket_port = int(arg)
                    except ValueError:
                        msg = messages.COMMAND_SERVER_INVALID_PORT.format(arg)

                        print(msg)
                        raise ValueError(msg)

        if not self.http and not self.websocket:
            self.http = True

    def run(self, args: List[str]) -> int:
        """
        Runs the server command. Will start the HTTP server on the default port with no arguments.

        :param args: List of arguments.
        :return: Command line exit code, defaults to SUCCESS.
        """

        try:
            self.parse_arguments(args)
        except ValueError:
            return self.invalid_arguments()

        initialize_logging(debug=self.debug)

        root_services = get_root_services()

        services_router = ServicesRouter(root_services.context_root, root_services.services)

        if self.http:
            http_thread = Thread(target=Server._run_http_server,
                                 kwargs={'router': services_router.http_router, 'port': self.http_port})
            http_thread.daemon = True
            http_thread.start()
            time.sleep(1)

        if self.websocket:
            websocket_thread = Thread(target=Server._run_websocket_server,
                                      kwargs={'router': services_router.websocket_router, 'port': self.websocket_port})
            websocket_thread.daemon = True
            websocket_thread.start()
            time.sleep(1)

        try:
            signal.signal(signal.SIGINT, Server._signal_handler)
        except ValueError:
            pass

        while self._http_server_running() or self._websocket_server_running():
            time.sleep(3)

        return exit_codes.SUCCESS


class Version(Command):
    """
    Version

    Command to retreive the installed version of limis.
    """
    help = 'Returns the current limis version'
    help_arguments = ''
    name = 'version'

    @classmethod
    def run(cls, args: List[str]) -> int:
        """
        Executes the version command.

        :param args: Arguments are not used for this command.
        :return: Command line exit code, defaults to SUCCESS.
        """
        print(messages.COMMAND_VERSION.format(get_version()))
        return exit_codes.SUCCESS
