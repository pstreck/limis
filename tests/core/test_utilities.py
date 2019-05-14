"""
limis core - utilities - tests
"""
import io
import logging
import os

from contextlib import redirect_stdout
from distutils.version import StrictVersion
from pathlib import Path
from shutil import copytree
from unittest import TestCase

import limis

from limis.core import environment
from limis.core.utilities import get_root_services, get_version, initialize_logging, replace_template_strings

from tests import remove_directory, remove_logfile, string_in_file


class TestMethods(TestCase):
    template_source_directory = Path(__file__).parent / 'data/templates'
    template_test_directory = Path(__file__).parent.parent / 'template_test'
    template_test_sub_directory = template_test_directory / 'template_test_sub'

    @staticmethod
    def _create_test_templates():
        copytree(str(TestMethods.template_source_directory), str(TestMethods.template_test_directory))
        copytree(str(TestMethods.template_test_directory), str(TestMethods.template_test_sub_directory))

    def tearDown(self):
        remove_logfile()

    def test_get_root_services(self):
        os.environ[environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE] = 'test_project'

        path = Path(__file__).parent / 'data/settings_root_services.ini'
        os.environ[environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE] = str(path)

        root_services = get_root_services()

        self.assertEqual(root_services.context_root, 'context_root')
        self.assertEqual(root_services.services, ['test'])

        os.environ.pop(environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE)
        os.environ.pop(environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)

    def test_get_root_services_with_invalid_type(self):
        with self.assertRaises(TypeError):
            get_root_services()

    def test_get_root_services_with_invalid_project(self):
        os.environ[environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE] = 'invalid_project'

        with self.assertRaises(AttributeError):
            get_root_services()

        os.environ.pop(environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE)

    def test_get_root_services_with_invalid_module(self):
        os.environ[environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE] = 'test_project'

        path = Path(__file__).parent / 'data/settings_root_services_invalid.ini'
        os.environ[environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE] = str(path)

        with self.assertRaises(ImportError):
            get_root_services()

        os.environ.pop(environment.LIMIS_PROJECT_NAME_ENVIRONMENT_VARIABLE)
        os.environ.pop(environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)

    def test_get_version(self):
        version = get_version()
        self.assertEqual(version, StrictVersion('.'.join(map(str, limis.VERSION))))

    def test_initialize_logging(self):
        initialize_logging()

    def test_initialize_logging_with_debug(self):
        with redirect_stdout(io.StringIO()):
            initialize_logging(debug=True)

        self.assertEqual(logging.getLogger().level, logging.DEBUG)
        self.assertEqual(logging.getLogger('limis').level, logging.DEBUG)

    def test_initialize_logging_with_invalid_logging_config_file(self):
        path = Path(__file__).parent / 'data/settings_logging.ini'

        os.environ[environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE] = str(path)

        with self.assertRaises(ValueError):
            initialize_logging()

        os.environ.pop(environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)

    def test_replace_template_strings(self):
        self._create_test_templates()

        replace_template_strings(TestMethods.template_test_directory, ['variable0', 'variable1'], ['test0', 'test1'])

        files = [
            str(TestMethods.template_test_directory / 'test'),
            str(TestMethods.template_test_sub_directory / 'test')
        ]

        for file in files:
            self.assertTrue(string_in_file(file, 'test0'))
            self.assertTrue(string_in_file(file, 'test1'))
            self.assertTrue(string_in_file(file, 'test0 - test1'))

        remove_directory(TestMethods.template_test_directory)

