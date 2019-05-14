import http

from limis.services import Service
from limis.services.components import Component
from limis.services.handlers import ComponentHandler
from limis.test import LimisServerTestCase

from tests import get_http_response


class TestComponentHandler(LimisServerTestCase):
    class TestComponentHandler(ComponentHandler):
        def get(self):
            self.write(self.component_class.__name__)

    def test_initialize(self):
        class TestComponent(Component):
            component_name = 'test'
            component_path = 'test'
            component_http_handler = TestComponentHandler.TestComponentHandler

        service = Service('service', components=[TestComponent])

        self.run_server(http_router=service.http_router)

        path = TestComponent.component_path
        http_response = get_http_response('localhost', LimisServerTestCase.http_port, 'GET', '/{}'.format(path))

        self.assertEqual(http.client.OK, http_response[0])
        self.assertEqual(TestComponent.__name__, http_response[1])
