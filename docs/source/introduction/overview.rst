########
Overview
########

Architecture
************
limis contains the several modules that make up the framework:

* core - Base functionality for loading settings and setting up framework and project specific logging.
* management - Command line tooling for creating projects and services as well as instantiating servers.
* server - HTTP and WebSocket server based on Tornado.
* services - Service definition, extensible components and routing capabilities.

core
====
The core module provides base functional support tools for creating a limis project. One of the basic parts of the core
module is :class:`limis.core.Settings`. This module is framework wide solution for managing framework and project
specific settings.

When you create a limis project a settings.ini file is also created in the project directory. This file will be loaded
into the Settings class automatically based on the project settings environment variable. Settings files are structured
INI formatted files. The INI format specifies a section and values for each section. These can the be loaded by
importing 'settings' from 'limis.core'. Sections are defined as dictionary attributes of the 'settings' object.

An additional functionality provided by the core module is to initialize logging facilities.
:meth:`limis.core.utilities.initialize_logging` configures the root and limis loggers. A default logging configuration
file is provided which enables console and file logging to 'limis.log' at the INFO level. This can be overwritten in a
limis project.

management
==========
The management module implements a command line interface for project creation, service creation within a project and
running a limis server. After installing limis the 'limis-management' command will be installed in your environment.
This command allows you to create a limis project. A limis project contains the 'management.py' command which is used
to create new services and start the limis server.

server
======
The server module provides a Tornado HTTP and WebSocket server. Servers are passed routers defined in the services
module and route requests appropriately.

services
========
The services module is the backbone of limis. It is composed of a service, components, handler and router. The
:class:`limis.services.Service` defines a service composed of components. Each service has a name and path. The service
generates a Tornado RuleRouter which maps URL routes to individual component handlers. There is a specific router for
HTTP and a specific router WebSockets.

The :class:`limis.services.components.Component` class implements a service component. A service component defines what
a service can do. This may be accessing resources, performing processes, handling events or other defined actions. Each
component has a name and path that are used for access and routing purposes. Components define service callable actions
with the 'action' decorator. Component has a built-in action called 'define' which generates a JSON object describing
the actions and attributes of a component. Component handlers provide a mapping to HTTP and WebSocket requests. A
default handler is provided :class:`limis.services.handlers.ComponentHandler`. ComponentHandler sets a instance variable
'component_class', this allows handler methods to access the component as needed.

Routing for services is done via :class:`limis.services.router.ServicesRouter`, this router is a container for multiple
service objects and generates a http_router and websocket_router. These are passed to the Server class when the server
is started from the management tool.