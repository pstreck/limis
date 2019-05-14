import http
import logging

from tornado.websocket import WebSocketHandler

from limis.services import messages
from limis.services import Service
from limis.services.components import Resource
from limis.services.handlers import ComponentHandler
from limis.test import LimisServerTestCase

from tests import get_http_response, send_websocket_message_and_get_response


class TestService(LimisServerTestCase):
    class TestHTTPRequestHandler(ComponentHandler):
        response = 'hello world'

        def get(self):
            self.write(self.response)

    class TestWebSocketHandler(ComponentHandler, WebSocketHandler):
        response_on_message = 'websocket message received: {}'

        def on_message(self, message):
            self.write_message(self.response_on_message.format(message))

    class TestResource(Resource):
        component_name = 'test_resource'
        component_path = 'test_resource'
        test_attribute = 'test attribute'

    class TestResource1(Resource):
        component_name = 'test_resource_1'
        component_path = 'test_resource_1'

    def setUp(self):
        self.logger = logging.getLogger('limis.services')

    def test_add_component(self):
        service = Service(name='service', components=[])

        with self.assertLogs(logger=self.logger, level='WARNING') as log:
            service.add_component(self.TestResource)

        self.assertTrue(log.output[0].find(
            messages.SERVICE_ADD_COMPONENT_WITH_NO_HANDLER.format(self.TestResource.component_name, 'service')))

    def test_add_component_with_invalid_component_class(self):
        service = Service(name='service', components=[])

        with self.assertRaises(ValueError):
            with self.assertLogs(logger=self.logger, level='ERROR') as log:
                service.add_component(Service)

        self.assertTrue(log.output[0].find(
            messages.SERVICE_ADD_COMPONENT_INVALID_COMPONENT_CLASS.format(Service.__name__)))

    def test_add_component_with_invalid_component_type(self):
        service = Service(name='service', components=[])

        with self.assertRaises(TypeError):
            with self.assertLogs(logger=self.logger, level='ERROR') as log:
                invalid_component = 'invalid_component'
                service.add_component(invalid_component)

        self.assertTrue(log.output[0].find(messages.SERVICE_ADD_COMPONENT_INVALID_COMPONENT_TYPE))

    def test_init(self):
        service = Service(name='service', components=[])

    def test_init_component_with_no_handler(self):
        test_response = '<html><title>404: Not Found</title><body>404: Not Found</body></html>'

        with self.assertLogs(logger=self.logger, level='WARNING') as log:
            service = Service(name='service', components=[self.TestResource])

        self.assertTrue(log.output[0].find(
            messages.SERVICE_ADD_COMPONENT_WITH_NO_HANDLER.format(self.TestResource.component_name, 'service')))

        self.run_server(http_router=service.http_router, websocket_router=service.websocket_router)

        path = self.TestResource.component_path

        http_response = get_http_response('localhost', LimisServerTestCase.http_port, 'GET', '/{}'.format(path))

        self.assertEqual(http.client.NOT_FOUND, http_response[0])
        self.assertEqual(test_response, http_response[1])

    def test_init_component_with_http_handler(self):
        class TestResourceWithHTTPHandler(self.TestResource):
            component_http_handler = self.TestHTTPRequestHandler

        service = Service(name='service', components=[TestResourceWithHTTPHandler])

        self.run_server(http_router=service.http_router)

        path = TestResourceWithHTTPHandler.component_path

        http_response = get_http_response('localhost', LimisServerTestCase.http_port, 'GET', '/{}'.format(path))

        self.assertEqual(http.client.OK, http_response[0])
        self.assertEqual(self.TestHTTPRequestHandler.response, http_response[1])

    def test_init_component_with_websocket_handler(self):
        class TestResourceWithWebSocketHandler(self.TestResource):
            component_websocket_handler = self.TestWebSocketHandler

        service = Service(name='service', components=[TestResourceWithWebSocketHandler])

        self.run_server(websocket_router=service.websocket_router)

        message = 'test'
        path = TestResourceWithWebSocketHandler.component_path

        websocket_response = send_websocket_message_and_get_response(
            'localhost', LimisServerTestCase.websocket_port, path, message)
        self.assertEqual(websocket_response, self.TestWebSocketHandler.response_on_message.format(message))

    def test_init_component_with_http_and_websocket_handler(self):
        class TestResourceWithBothHandlers(self.TestResource):
            component_http_handler = self.TestHTTPRequestHandler
            component_websocket_handler = self.TestWebSocketHandler

        service = Service(name='service', components=[TestResourceWithBothHandlers])

        self.run_server(http_router=service.http_router, websocket_router=service.websocket_router)

        path = TestResourceWithBothHandlers.component_path

        http_response = get_http_response('localhost', LimisServerTestCase.http_port, 'GET', '/{}'.format(path))

        self.assertEqual(http.client.OK, http_response[0])
        self.assertEqual(self.TestHTTPRequestHandler.response, http_response[1])

        message = 'test'

        websocket_response = send_websocket_message_and_get_response(
            'localhost', LimisServerTestCase.websocket_port, path, message)
        self.assertEqual(websocket_response, self.TestWebSocketHandler.response_on_message.format(message))

    def test_init_multiple_components_with_http_and_websocket_handler(self):
        class TestResourceWithBothHandlers(self.TestResource):
            component_http_handler = self.TestHTTPRequestHandler
            component_websocket_handler = self.TestWebSocketHandler

        class TestResource0(TestResourceWithBothHandlers):
            component_name = 'test_resource_0'
            component_path = 'test_resource_0'

        class TestResource1(TestResourceWithBothHandlers):
            component_name = 'test_resource_1'
            component_path = 'test_resource_1'

        service = Service(name='service', components=[TestResource0, TestResource1])

        self.run_server(http_router=service.http_router, websocket_router=service.websocket_router)

        paths = [TestResource0.component_path, TestResource1.component_path]
        message = 'test'

        for path in paths:
            http_response = get_http_response('localhost', LimisServerTestCase.http_port, 'GET', '/{}'.format(path))
            self.assertEqual(http.client.OK, http_response[0])
            self.assertEqual(self.TestHTTPRequestHandler.response, http_response[1])

            websocket_response = send_websocket_message_and_get_response(
                'localhost', LimisServerTestCase.websocket_port, path, message)
            self.assertEqual(websocket_response, self.TestWebSocketHandler.response_on_message.format(message))
