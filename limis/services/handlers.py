"""
limis server - handlers

Component handlers.
"""
from typing import Type

from tornado.web import RequestHandler

from limis.services import Component


class ComponentHandler(RequestHandler):
    """
    Generic component handler.

    Initialization sets the component class which can be accessed from request methods.

    .. note::
        WebSocket handlers should inherit from ComponentHandler and tornado.websocket.WebSocketHandler.

    """
    def initialize(self, component_class: Type[Component]):
        """
        Initializes request handler, called before request handler http method.

        :param component_class: The class of the component which the handler is assigned to.
        """
        self.component_class = component_class
