limis - light microservices
===========================
`limis <https://limis.io>`_ is a framework for creating microservices on a ligh flexible platform. A RESTful approach
to services is followed. In addition to traditional HTTP services a WebSocket transport is provided. WebSockets are
highly beneficial for services due to their two-way communication pattern and single socket connection for multiple
calls.

`Tornado <https://www.tornadoweb.org>`_ provides the communication backbone for limis, The Tornado framework enables
limis to build services on a well established transport platform.

.. warning:: limis is currently an alpha release. There may be significant bugs, and class, methods, variable names may
    change prior to the beta release.

.. toctree::
    :maxdepth: 2
    :caption: Introduction

    introduction/overview
    introduction/installation
    introduction/management

.. toctree::
    :maxdepth: 2
    :caption: Module API

    modules/core
    modules/management
    modules/server
    modules/services
