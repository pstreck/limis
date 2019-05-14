##########
Management
##########

limis management
****************

limis includes a command line tool for managing projects. 'limis-management'. This can be used to create scaffolding for
a new limis project. Run this command from a terminal and specify the 'create_project' command with an optional project
directory.

.. code-block:: console

    limis-management create_project <project_name>

project management
******************

Projects created by the 'limis-management' command include a 'management.py' script. This script can be used to create
service scaffolding, or start the limis server.

create service
==============

.. code-block:: console

    cd <project_name>
    python management.py create_service <service_name>

start server
============

.. code-block:: console

    python manage.py server --http --websocket

.. note::
    The server listner ports may also be specified with the additional '--http_port' and '--websocket_port' options. See
    :class:`limis.management.commands.Server` for additional details.
