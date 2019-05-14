"""
limis core - utilities

Utility functions.
"""
import fileinput
import glob
import logging
import logging.config
import os
import re

from distutils.version import StrictVersion
from importlib import import_module
from pathlib import Path
from typing import List, Type

from limis import VERSION
from limis.core import messages
from limis.core import Settings
from limis.core.environment import LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE


def get_root_services() -> Type:
    """
    Returns the root services module as defined in settings. Settings attribute is set by the
    "<project_name>['root_services']" value. LIMIS_PROJECT_NAME environment variable is used to set the project_name'.

    :raises AttributeError: Error indicating the project is invalid.
    :raises TypeError: Error indicating root services is an invalid type.
    :raises ImportError: Error indicating the root services module could not be imported.
    :returns: Imported module.
    """
    project_name = os.environ.get(LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE)

    try:
        root_services_name = getattr(Settings(), project_name)['root_services']
    except AttributeError:
        raise AttributeError(messages.GET_ROOT_SERVICES_INVALID_PROJECT_ERROR.format(project_name))
    except TypeError:
        raise TypeError(messages.GET_ROOT_SERVICES_INVALID_PROJECT_NAME_TYPE)

    try:
        module = import_module(root_services_name)
    except ImportError:
        raise ImportError(messages.GET_ROOT_SERVICES_IMPORT_ERROR.format(root_services_name))

    return module


def get_version() -> str:
    """
    Retrieves the limis version.

    :return: String with the strict current version
    """
    return str(StrictVersion('.'.join(map(str, VERSION))))


def initialize_logging(debug: bool = False):
    """
    Initializes logging for the application.

    The logging configuration file is determined by the logging['config_file'] setting.

    :param debug: Flag to enable debugging mode.
    :raises ValueError: Error indicating specified logging configuration file does not exist
    """
    logging_config_file = Settings().logging['config_file']

    path = Path(logging_config_file)
    if not path.exists():
        path = Path(__file__).parent / logging_config_file

        if not path.exists():
            raise ValueError(messages.LOGGING_CONFIG_FILE_NOT_FOUND.format(logging_config_file))

    logging.config.fileConfig(str(path))

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('limis').setLevel(logging.DEBUG)

    logging.getLogger(__name__).debug(messages.LOGGING_INITIALIZED)


def replace_template_strings(directory: Path, template_strings: List[str], value_strings: List[str]):
    """
    Replaces template strings with values for all files in a directory. Recursively process all files in the target
    directory and replaces strings wihin files ending with the '.tpl' extension.

    :param directory: Directory with files to replace template strings.
    :param template_strings: List of template strings to replace, should be name only without template {{}}
    characters.
    :param value_strings: List of strings to replace template strings with.
    """
    cwd = Path.cwd()
    os.chdir(str(directory))

    for entry in glob.iglob(str(directory) + '/**', recursive=True):
        if not os.path.isdir(entry) and entry.endswith('tpl'):
            with fileinput.FileInput(entry, inplace=True) as file:
                for line in file:
                    new_line = line

                    for i in enumerate(template_strings):
                        template_string = i[1]
                        value_string = value_strings[i[0]]

                        regex = '{{%s}}' % template_string
                        new_line = re.sub(regex, value_string, new_line)

                    print(new_line, end='')

            Path(entry).rename(entry.split('.tpl')[0])

    os.chdir(str(cwd))
