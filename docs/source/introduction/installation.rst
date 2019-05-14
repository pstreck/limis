##############################
Installation and Project Setup
##############################

Installation
************
.. code-block:: console

    pip install limis

Project Setup
*************

Project Creation
================
.. code-block:: console

    limis-management create_project <project_name>

Service Creation
================
* Scaffold the services with the project management command:

.. code-block:: console

    cd <project_name>
    python management.py create_service <service_name>

* Create a request handler to route service requests to your component in '<service_name>/handlers.py':

.. code-block:: python

    from typing import Union

    from tornado.websocket import WebSocketHandler
    from limis.services.handlers import ComponentHandler


    class HelloHTTPHandler(ComponentHandler):
        def get(self):
            self.write(self.component_class().hello())


    class HelloWebSocketHandler(ComponentHandler, WebSocketHandler):
        def on_message(self, message: Union[str, bytes]):
            self.write_message(self.component_class().hello())

* Create a component to perform actions on requests in '<service_name>/components.py':

.. code-block:: python

    from limis.services.components import Component

    from hello.handlers import HelloHTTPHandler, HelloWebSocketHandler


    class HelloComponent(Component):
        component_name = 'hello'
        component_path = 'hello'
        component_http_handler = HelloHTTPHandler
        component_websocket_handler = HelloWebSocketHandler

        def hello(self):
            return 'hello'

* Create a services configuration entry in '<service_name>'/services.py:

.. code-block:: python

    from limis.services import Service

    from hello.components import HelloComponent


    services = [
        Service(name='hello', path='hello', components=[HelloComponent]),
    ]

* Add your services module to the project services configuration '<project_name>/services.py':

.. code-block:: python

    from hello.services import services as hello_services


    context_root = ''
    services = hello_services

Launch Server
=============
Launch the limis server from the command prompt:

.. code-block:: console

    python manage.py server --http --websocket

Test Service
------------

* HTTP Service

.. code-block:: console

    curl http://localhost:8080/hello/hello

Output:

.. code-block:: console

    hello

* WebSocket Service

Example using `websocket-client <https://github.com/websocket-client/websocket-client>`_

.. code-block:: python

    from websocket import create_connection
    websocket = create_connection('ws://localhost:8888/hello/hello/')
    websocket.send('test')
    websocket.recv()

Output:

.. code-block:: console

    hello