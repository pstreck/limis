#!/usr/bin/env python
import os

LIMIS_IMPORT_ERROR = 'Unable to import limis. Please ensure it is installed within your current environment.'

name = '{{name}}'

os.environ['LIMIS_PROJECT_NAME'] = name
os.environ['LIMIS_PROJECT_SETTINGS'] = '{}/settings.ini'.format(name)

if __name__ == '__main__':
    try:
        from limis.management import execute_limis_project_management
    except ImportError:
        execute_limis_project_management = None
        print(LIMIS_IMPORT_ERROR)
        exit(2)

    exit(execute_limis_project_management())
