"""
limis core - init - tests
"""
import os

from pathlib import Path
from unittest import TestCase

from limis.core import environment, Settings


class TestSettings(TestCase):
    def test_init(self):
        settings_instance = Settings()

    def test_init_with_invalid_File(self):
        with self.assertRaises(ValueError):
            settings_instance = Settings(['invalid_file'])

    def test_init_with_additional_settings_file(self):
        path = Path(__file__).parent / 'data/settings.ini'
        settings_instance = Settings([str(path)])

        self.assertTrue(hasattr(settings_instance, 'test_settings'))
        self.assertEqual(settings_instance.test_settings['valid_setting'], 'valid')
        self.assertFalse(hasattr(settings_instance, 'nonexistent_setting'))

    def test_init_with_project_settings_file(self):
        path = Path(__file__).parent / 'data/settings.ini'
        os.environ[environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE] = str(path)

        settings_instance = Settings()
        self.assertEqual(settings_instance.test_settings['valid_setting'], 'valid')

        os.environ.pop(environment.LIMIS_PROJECT_SETTINGS_ENVIRONMENT_VARIABLE)
