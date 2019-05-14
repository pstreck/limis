import io
from setuptools import find_packages, setup

from limis.core.utilities import get_version

with io.open('README.rst', 'rt', encoding='utf8') as file:
    readme = file.read()

setup(
    name='limis',
    version=get_version(),
    author='Philip Streck',
    author_email='philip@limis.io',
    license='MIT',
    description='light microservice solution',
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    url='https://limis.io',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.5',
    scripts=['limis/bin/limis-management.py'],
    entry_points={'console_scripts': [
        'limis-management = limis.management:execute_limis_management',
    ]},
    install_requires=[
        'tornado',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
