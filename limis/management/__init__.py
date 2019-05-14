"""
limis management

Defines a command line interface framework for working with limis projects.
"""
import sys

from limis.management import exit_codes, messages
from limis.management.commands import CreateProject, CreateService, Server, Version


class CommandLineInterface:
    """
    CommandLineInterface

    Provides command line utility functionality for limis.

    :attribute commands: Class attribute with a list of installed Command classes.
    """
    commands = [
        Version
    ]

    @classmethod
    def __help(cls) -> int:
        """
        Displays help text for each installed command.

        :return: Command line exit code, default SUCCESS.
        """
        print(messages.COMMAND_LINE_INTERFACE_HELP_COMMAND.format('help', 'Displays helpful information'))

        for command in cls.commands:
            print(messages.COMMAND_LINE_INTERFACE_HELP_COMMAND.format(command.name, command.help))

        return exit_codes.SUCCESS

    @classmethod
    def run(cls) -> int:
        """
        Runs a command, first argument in the list provided must be the command name followed by an arguments to be
        passed to the command.

        :return: Command line exit code, exit codes are defined in the management.exit_codes module.
        """
        args = sys.argv[1:]

        if len(args) == 0:
            print(messages.COMMAND_LINE_INTERFACE_COMMAND_REQUIRED)
            return cls.__help()

        command_name = args.pop(0)

        if command_name == 'help':
            return cls.__help()

        for command in cls.commands:
            if command.name == command_name:
                return command().run(args)

        print(messages.COMMAND_LINE_INTERFACE_RUN_UNKNOWN_COMMAND.format(command_name))

        return exit_codes.UNKNOWN_COMMAND


class LimisManagement(CommandLineInterface):
    """
    Defines the command line interface commands for system level management.
    """
    commands = [
        Version,
        CreateProject
    ]


class LimisProjectManagement(CommandLineInterface):
    """
    Defines the command line interface commands for project level management.
    """
    commands = [
        CreateService,
        Server,
        Version
    ]


def execute_limis_management() -> int:
    """
    Executes the limis management command line interface.

    :return: Returns the results of the command line interface run.
    """
    return LimisManagement.run()


def execute_limis_project_management() -> int:
    """
    Executes the limis project management command line interface.

    :return: Returns the results of the command line interface run.
    """
    return LimisProjectManagement.run()
