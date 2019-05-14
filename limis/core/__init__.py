"""
limis core

Provides solution wide functionality for managing logging, settings, applications, etc.
"""
import os

from configparser import ConfigParser
from pathlib import Path
from setuptools import find_packages
from typing import List

from limis.core import messages
from limis.core.environment import LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE


class Settings:
    """
    Settings for global application

    Most packages defined within limis have a settings.ini file and the default settings are loaded for each of those
    modules. Settings may be overwritten by passing additional settings files to the class initialization method.
    Additional settings files specified are loaded after limis modules. Limis packages without settings.ini are
    ignored, modules passed with additional_settings_files or the environment variable that do not exist will raise
    an error.

    Project specific settings are loaded from the environment variable "LIMIS_PROJECT_SETTINGS".

    Settings are loaded as attributes of instantiated Settings class. Each attribute name represents a section and is
    a dictionary of settings values.
    """
    def __init__(self, additional_settings_files: List[str] = None):
        """
        Initializes the Settings class.

        :param additional_settings_files: List of additional settings modules to load in addition to built-ins
        """
        self._limis_path = Path(__file__).parent.parent
        self._settings_files = [
            self._limis_path / package / 'settings.ini' for package in find_packages(str(self._limis_path))
        ]

        if additional_settings_files:
            additional_settings_files_as_paths = [Path(settings_file) for settings_file in additional_settings_files]
            self._settings_files = self._settings_files + additional_settings_files_as_paths

        project_settings_file = os.environ.get(LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)

        if project_settings_file:
            self._settings_files = self._settings_files + [Path(project_settings_file)]

        self.load_settings()

    def load_settings(self):
        """
        Loads settings from settings files.

        :raises ValueError: Error indicating one of the settings file was not found.
        """
        for settings_file in self._settings_files:
            if settings_file.exists():
                config = ConfigParser()
                config.read(str(settings_file))

                for section in config:
                    config_settings = {}

                    for setting in config[section]:
                        config_settings[setting] = config[section][setting]

                    setattr(self, section, config_settings)
            elif not str(settings_file).startswith(str(self._limis_path)):
                raise ValueError(messages.SETTINGS_LOAD_SETTINGS_FILE_NOT_FOUND.format(settings_file))


settings = Settings()
