import io
import os
import signal
import time

from contextlib import redirect_stdout
from pathlib import Path
from threading import Thread
from typing import List
from unittest import TestCase

from limis.core import environment, settings
from limis.management import exit_codes
from limis.management.commands import Command, CreateProject, CreateService, Server, Version

from tests import listening, remove_directory, string_in_file


class TestCommand(TestCase):
    def test_invalid_arguments(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(Command.invalid_arguments(), exit_codes.INVALID_ARGUMENTS)


class TestCreateProject(TestCase):
    test_project_name = 'test_project'
    test_project_default_directory = Path.cwd() / 'test_project'
    test_project_directory = Path.cwd() / 'test_project_directory'

    def _validate_test_run(self, name: str, directory: Path):
        self.assertTrue(directory.exists())
        self.assertTrue((directory / name).exists())

        self.assertTrue(string_in_file(str(directory / 'management.py'), 'name = \'{}\''.format(name)))

    def tearDown(self):
        remove_directory(self.test_project_directory)
        remove_directory(self.test_project_default_directory)

    def test_run(self):
        name = self.test_project_name
        directory = self.test_project_default_directory

        command = CreateProject()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name, directory]), exit_codes.SUCCESS)

        self._validate_test_run(name, directory)

    def test_run_with_directory(self):
        name = self.test_project_name
        directory = self.test_project_directory

        command = CreateProject()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name, str(directory)]), exit_codes.SUCCESS)

        self._validate_test_run(name, directory)

    def test_run_with_existing_directory(self):
        name = self.test_project_name
        directory = self.test_project_default_directory

        command = CreateProject()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name, directory]), exit_codes.SUCCESS)
            self.assertEqual(command.run([name, directory]), exit_codes.ERROR_CREATING_PROJECT)

    def test_run_with_invalid_arguments(self):
        command = CreateProject()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([]), exit_codes.INVALID_ARGUMENTS)


class TestCreateService(TestCase):
    test_service_name = 'test_service'
    test_service_path = 'test_service_path'
    test_service_default_directory = Path.cwd() / 'test_service'
    test_service_directory = Path.cwd() / 'test_service_path'

    def _validate_test_run(self, name: str, directory: Path):
        self.assertTrue(directory.exists())

        self.assertTrue(string_in_file(str(directory / 'services.py'),
                                       'Service(name=\'{}\', path=\'{}\', components=[]),'.format(name, name)))

    def tearDown(self):
        remove_directory(self.test_service_default_directory)
        remove_directory(self.test_service_directory)

    def test_run(self):
        name = self.test_service_name
        directory = self.test_service_default_directory

        command = CreateService()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name]), exit_codes.SUCCESS)

        self._validate_test_run(name, directory)

    def test_run_with_directory(self):
        name = self.test_service_name
        directory = self.test_service_directory

        command = CreateService()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name, str(directory)]), exit_codes.SUCCESS)

        self._validate_test_run(name, directory)

    def test_run_with_existing_directory(self):
        name = self.test_service_name

        command = CreateService()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([name]), exit_codes.SUCCESS)
            self.assertEqual(command.run([name]), exit_codes.ERROR_CREATING_SERVICE)

    def test_run_with_invalid_arguments(self):
        command = CreateService()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run([]), exit_codes.INVALID_ARGUMENTS)


class TestServer(TestCase):
    project_name = 'test_project'
    project_directory = Path.cwd() / project_name

    @staticmethod
    def __run_command(args: List[str]):
        global server_command

        server_command = Server()

        with redirect_stdout(io.StringIO()):
            server_command.run(args=args)

    @classmethod
    def setUpClass(cls):
        command = CreateProject()

        with redirect_stdout(io.StringIO()):
            command.run([cls.project_name])

        settings_file = cls.project_directory / cls.project_name / 'settings.ini'

        os.environ[environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE] = cls.project_name
        os.environ[environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE] = str(settings_file)

        if settings_file.exists():
            settings_file.unlink()

        with open(str(settings_file), 'w') as file:
            print('[test_project]', file=file)
            print('root_services={}.{}.services'.format(cls.project_name, cls.project_name), file=file)

    @classmethod
    def tearDownClass(cls):
        remove_directory(cls.project_directory)

        os.environ.pop(environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE)
        os.environ.pop(environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)

    def setUp(self):
        try:
            del server_command
        except NameError:
            pass

    def tearDown(self):
        try:
            if server_command._http_server_running() or server_command._websocket_server_running():
                server_command._signal_handler(signal.SIGINT, None)

                while server_command._http_server_running() or server_command._websocket_server_running():
                    time.sleep(3)
        except NameError:
            pass

    def test__http_server_running(self):
        self.assertFalse(Server._http_server_running())

    def test__websocket_server_running(self):
        self.assertFalse(Server._websocket_server_running())

    def test__signal_handler(self):
        Server._signal_handler(signal.SIGINT, None)

    def test_parse_arguments_none(self):
        command = Server()
        command.parse_arguments(args=[])
        self.assertTrue(command.http)

    def test_parse_arguments_debug(self):
        command = Server()
        command.parse_arguments(args=['-d'])
        self.assertTrue(command.debug)

        command = Server()
        command.parse_arguments(args=['--debug'])
        self.assertTrue(command.debug)

    def test_parse_arguments_http(self):
        command = Server()
        command.parse_arguments(args=['-p'])
        self.assertTrue(command.http)

        command = Server()
        command.parse_arguments(args=['--http'])
        self.assertTrue(command.http)

    def test_parse_arguments_http_port(self):
        command = Server()
        command.parse_arguments(['--http_port', '8000'])
        self.assertEqual(command.http_port, 8000)

        command = Server()
        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                command.parse_arguments(['--http_port', 'invalid'])

        command = Server()
        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                command.parse_arguments(['--http_port'])

    def test_parse_arguments_websocket(self):
        command = Server()
        command.parse_arguments(args=['-w'])
        self.assertTrue(command.websocket)

        command = Server()
        command.parse_arguments(args=['--websocket'])
        self.assertTrue(command.websocket)

    def test_parse_arguments_websocket_port(self):
        command = Server()
        command.parse_arguments(['--websocket_port', '8000'])
        self.assertEqual(command.websocket_port, 8000)

        command = Server()
        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                command.parse_arguments(['--websocket_port', 'invalid'])

        command = Server()
        with self.assertRaises(ValueError):
            with redirect_stdout(io.StringIO()):
                command.parse_arguments(['--websocket_port'])

    def test_run(self):
        thread = Thread(target=self.__run_command, kwargs={'args': []})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(int(settings.server['default_http_port'])))

    def test_run_invalid_arguments(self):
        command = Server()

        with redirect_stdout(io.StringIO()):
            self.assertEqual(command.run(args=['--http_port', 'invalid']), exit_codes.INVALID_ARGUMENTS)

    def test_run_http(self):
        thread = Thread(target=self.__run_command, kwargs={'args': ['-p']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(int(settings.server['default_http_port'])))

    def test_run_http_with_port(self):
        thread = Thread(target=self.__run_command, kwargs={'args': ['-p', '--http_port=8001']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(8001))

    def test_run_websocket(self):
        thread = Thread(target=self.__run_command, kwargs={'args': ['-w']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(int(settings.server['default_websocket_port'])))

    def test_run_websocket_with_port(self):
        thread = Thread(target=self.__run_command, kwargs={'args': ['-w', '--websocket_port=8001']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(8001))

    def test_run_http_and_websocket(self):
        thread = Thread(target=self.__run_command, kwargs={'args': ['-p', '-w']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(int(settings.server['default_http_port'])))
        self.assertTrue(listening(int(settings.server['default_websocket_port'])))

    def test_run_http_and_websocket_with_ports(self):
        thread = Thread(target=self.__run_command,
                        kwargs={'args': ['-p', '--http_port=8001', '-w', '--websocket_port=8002']})
        thread.daemon = True
        thread.start()
        time.sleep(2)

        self.assertTrue(listening(8001))
        self.assertTrue(listening(8002))


class TestVersion(TestCase):
    def test_run(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(Version.run(args=[]), exit_codes.SUCCESS)
