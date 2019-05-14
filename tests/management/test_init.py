import io
import sys
from contextlib import redirect_stdout
from unittest import TestCase

from limis.management import CommandLineInterface, execute_limis_management, execute_limis_project_management, \
    exit_codes


class TestCaseWithSysArgumentOverride(TestCase):
    def setUp(self):
        self.original_sys_argv = sys.argv

    def tearDown(self):
        sys.argv = self.original_sys_argv


class TestCommandLineInterface(TestCaseWithSysArgumentOverride):
    def test_run(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]]
            self.assertEqual(CommandLineInterface.run(), exit_codes.SUCCESS)

    def test_run_with_help_command(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]] + ['help']
            self.assertEqual(CommandLineInterface.run(), exit_codes.SUCCESS)

    def test_run_with_unknown_command(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]] + ['unknown_command']
            self.assertEqual(CommandLineInterface.run(), exit_codes.UNKNOWN_COMMAND)

    def test_run_with_version_command(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]] + ['version']
            self.assertEqual(CommandLineInterface.run(), exit_codes.SUCCESS)


class TestMethods(TestCaseWithSysArgumentOverride):
    def test_execute_limis_management(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]]
            self.assertEqual(execute_limis_management(), exit_codes.SUCCESS)

    def test_execute_limis_project_management(self):
        with redirect_stdout(io.StringIO()):
            sys.argv = [self.original_sys_argv[0]]
            self.assertEqual(execute_limis_project_management(), exit_codes.SUCCESS)
