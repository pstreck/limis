limis
=====
.. image:: https://travis-ci.org/limis-project/limis.svg?branch=master
    :alt: limis build status
    :target: https://travis-ci.org/limis-project/limis

.. image:: https://codecov.io/gh/limis-project/limis/branch/master/graph/badge.svg
    :alt: limis coverage status
    :target: https://codecov.io/gh/limis-project/limis

limis is a light microservice framework built in `Python <https://www.python.org/>`_ and powered by
`Tornado <https://www.tornadoweb.org/>`_.

.. warning::
    The project is currently in active development and should be considered alpha grade at the moment. Features are
    being added and removed and expect the API to change frequently. Release 0.1 is targeted to be a more stable
    release.

Examples: limis examples can be found on github at `limis_examples <https://github.com/limis-project/limis_examples>`_

Architecture
------------
Handler - Component - Controller
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
limis services are built with using the handler - component controller design pattern, or hcc. hcc is an architectural
design pattern used for developing services with structure, reuse an rapid deployment in mind. Handler - component -
controller is similar in design to the commonly used
`model - view - controller <(https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller>`_ pattern used for
developing graphical user interfaces and web applications.

.. image:: https://limis.io/handler-component-controller.svg
    :alt: limis component

Component
~~~~~~~~~
Components within limis are called by a handler to perform an action. When an action is called the component invokes the
appropriate controller. The controller processes the request data and carries out operations such as model manipulation,
business process, or other defined operation. A push controller may also call an action on a component to push an event
driven message to the consumer. Components are stateless, but may receive state and pass that information to a
controller. Component interceptors provide a facility for hooks that are applied to all actions. Some interceptors
built into limis are facilities for authorization, caching, request validation and logging.

.. image:: https://limis.io/component.svg
    :alt: limis component

Deployment Pattern
~~~~~~~~~~~~~~~~~~
Deployment can be done in multiple ways. limis is designed without a specific cloud vendor in mind and is capable of
running in container model or serverless model. Services may be bundled into a single run-time container to optimize
cloud usage. A service registry performs discovery at the client and server side and an API gateway provides
authentication and routing.

.. image:: https://limis.io/deployment-pattern.svg
    :alt: limis deployment pattern

Instructions
------------

Installation
~~~~~~~~~~~~
.. code-block::

    pip install limis

Project Creation
~~~~~~~~~~~~~~~~
.. code-block::

    limis-management create_project <project_name>

Service Creation
~~~~~~~~~~~~~~~~
* Scaffold the services with the project management command:

.. code-block::

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
~~~~~~~~~~~~~
Launch the limis server from the command prompt:

.. code-block::

    python manage.py server --http --websocket

Test Service
~~~~~~~~~~~~

* HTTP Service

.. code-block::

    curl http://localhost:8080/hello/hello

Output:

.. code-block::

    hello

* WebSocket Service

Example using `websocket-client <https://github.com/websocket-client/websocket-client>`_

.. code-block:: python

    from websocket import create_connection
    websocket = create_connection('ws://localhost:8888/hello/hello/')
    websocket.send('test')
    websocket.recv()

Output:

.. code-block::

    hello