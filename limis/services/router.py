"""
limis services - router

Services router to generate URL routers between services.
"""
import logging

from typing import Dict, List

from tornado.routing import PathMatches, Rule, RuleRouter

from limis.services import Service
from limis.services import messages


class ServicesRouter:
    """
    Services Router
    """
    def __init__(self, path: str, services: List[Service] = None):
        """
        Initializes the router with the path specified. Path should be a string without leading or trailing '/'s. An
        optional list of Service objects may be provided to build the initial rules and routers.

        :param path: Path string, will be translated to '/<path>.*' for rule matching.
        :param services: List of Service objects to initialize the router with.
        """
        self.logger = logging.getLogger(__name__)
        self.path = path
        self._services = {}
        self._path_rule = '/{}.*'.format(self.path)

        self._http_router_rules = []
        self._websocket_router_rules = []

        if services:
            for service in services:
                self.add_service(service)

        self._http_router = None
        self._websocket_router = None

        self._build_routers()

    def _build_routers(self):
        """
        Builds the http and websocket routers. Routers are instances of Tornado RuleRouter.
        """
        self.logger.debug(messages.ROUTER_BUILD_ROUTERS)

        self._http_router = RuleRouter(self._http_router_rules)
        self._websocket_router = RuleRouter(self._websocket_router_rules)

    def _build_router_rules(self):
        """
        Builds the router rules. Each service is registered to the path configured in the Service object. Rules are
        created for both http and websocket routers and set to the rules objects of the router.
        """
        self.logger.debug(messages.ROUTER_BUILD_ROUTER_RULES)

        http_rules = []
        websocket_rules = []

        for name in sorted(self._services):
            service = self._services[name]

            path = '/{}/.*'.format(service.path)

            self.logger.debug(messages.ROUTER_BUILD_ROUTER_RULES_ADD_SERVICE.format(service.name, path))
            http_rules.append(Rule(PathMatches(path), service.http_router))
            websocket_rules.append(Rule(PathMatches(path), service.websocket_router))

        self._http_router_rules = http_rules
        self._websocket_router_rules = websocket_rules

    @property
    def path_rule(self) -> str:
        """
        Property to return the router path rule.

        :return: path
        """
        return self._path_rule

    @property
    def http_router(self) -> RuleRouter:
        """
        Property to return the http router.

        :return: http_router
        """
        return self._http_router

    @property
    def websocket_router(self) -> RuleRouter:
        """
        Property to return the websocket router

        :return: websocket_router
        """
        return self._websocket_router

    @property
    def http_router_rules(self) -> List[Rule]:
        """
        Property to return the http router rules

        :return: http_router_rules
        """
        return self._http_router_rules

    @property
    def websocket_router_rules(self) -> List[Rule]:
        """
        Property to return the http router rules

        :return: websocket_router_rules
        """
        return self._websocket_router_rules

    @property
    def services(self) -> Dict[str, Service]:
        """
        Property to return registered services dictionary

        :return: services
        """
        return self._services

    def add_service(self, service: Service):
        """
        Registers a service with the router, if service was registered successfully router will rebuild routing rules.
        The 'name' variable of the Service class is used as the key stored in the registry. This should be unique for
        your service.

        :param service: Service object to register
        :raises ValueError: Error indicating the service has already been registered.
        """
        self.logger.debug(messages.ROUTER_ADD_SERVICE.format(service.name))

        if service.name not in self._services:
            self._services[service.name] = service
        else:
            msg = messages.ROUTER_ADD_SERVICE_ALREADY_REGISTERED.format(service.name)

            self.logger.error(msg)
            raise ValueError(msg)

        self._build_router_rules()

    def get_service(self, name: str) -> Service:
        """
        Retrieves a service from the registry, service is looked up by name provided.

        :param name: Service name
        :return: Service object
        :raises ValueError: Error indicating the specified service name is not registered.
        """
        self.logger.debug(messages.ROUTER_GET_SERVICE.format(name))

        if name in self._services:
            return self._services[name]
        else:
            msg = messages.ROUTER_GET_REMOVE_SERVICE_NOT_REGISTERED.format(name)

            self.logger.error(msg)
            raise ValueError(msg)

    def remove_service(self, name: str):
        """
        Removes a service from the registry, if service was registered successfully router will rebuild routing rules.

        :param name: Service name
        :raises ValueError: Error indicating the specified service name is not registered.
        """
        self.logger.debug(messages.ROUTER_REMOVE_SERVICE.format(name))

        if name in self._services:
            self._services.pop(name)
        else:
            msg = messages.ROUTER_GET_REMOVE_SERVICE_NOT_REGISTERED.format(name)

            self.logger.error(msg)
            raise ValueError(msg)

        self._build_router_rules()
