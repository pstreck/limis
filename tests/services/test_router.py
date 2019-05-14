from unittest import TestCase

from tornado.routing import Rule, RuleRouter

from limis.services.router import Service, ServicesRouter


class TestServicesRouter(TestCase):
    def test_init(self):
        router = ServicesRouter('path')

        self.assertEqual(router.path, 'path')

    def test_init_with_services(self):
        service1 = Service('service1', [])
        service2 = Service('service2', [])

        router = ServicesRouter('path', [service1, service2])

        self.assertEqual(len(router.services), 2)

    def test__build_routers(self):
        service1 = Service('service1', [])
        service2 = Service('service2', [])

        router = ServicesRouter('path')
        router.add_service(service1)
        router.add_service(service2)
        router._build_routers()

        self.assertTrue(isinstance(router.http_router, RuleRouter))
        self.assertTrue(isinstance(router.websocket_router, RuleRouter))

    def test__build_router_rules(self):
        service1 = Service('service1', [])
        service2 = Service('service2', [])

        router = ServicesRouter('path')
        router.add_service(service1)
        router.add_service(service2)
        router._build_router_rules()

        self.assertEqual(len(router.http_router_rules), 2)
        self.assertEqual(router.http_router_rules[0].matcher._path, '/{}/.*'.format(service1.path))
        self.assertEqual(router.http_router_rules[0].target, service1.http_router)
        self.assertEqual(router.http_router_rules[1].matcher._path, '/{}/.*'.format(service2.path))
        self.assertEqual(router.http_router_rules[1].target, service2.http_router)

        self.assertEqual(len(router.websocket_router_rules), 2)
        self.assertEqual(router.websocket_router_rules[0].matcher._path, '/{}/.*'.format(service1.path))
        self.assertEqual(router.websocket_router_rules[0].target, service1.http_router)
        self.assertEqual(router.websocket_router_rules[1].matcher._path, '/{}/.*'.format(service2.path))
        self.assertEqual(router.websocket_router_rules[1].target, service2.http_router)

        self.assertTrue(isinstance(router.http_router, RuleRouter))
        self.assertTrue(isinstance(router.websocket_router, RuleRouter))

    def test_path_rule(self):
        router = ServicesRouter('path')
        self.assertEqual(router.path_rule, '/path.*')

    def test_http_router(self):
        router = ServicesRouter('path')
        self.assertTrue(isinstance(router.http_router, RuleRouter))

    def test_websocket_router(self):
        router = ServicesRouter('path')
        self.assertTrue(isinstance(router.websocket_router, RuleRouter))

    def test_http_router_rules(self):
        service1 = Service('service1', [])
        router = ServicesRouter('path', [service1])
        self.assertEqual(len(router.http_router_rules), 1)
        self.assertTrue(isinstance(router.http_router_rules[0], Rule))

    def test_websocket_router_rules(self):
        service1 = Service('service1', [])
        router = ServicesRouter('path', [service1])
        self.assertEqual(len(router.websocket_router_rules), 1)
        self.assertTrue(isinstance(router.websocket_router_rules[0], Rule))

    def test_services(self):
        service1 = Service('service1', [])
        router = ServicesRouter('path', [service1])
        self.assertEqual(len(router.services), 1)
        self.assertEqual(router.services[service1.name], service1)

    def test_add_service(self):
        router = ServicesRouter('path')
        service1 = Service('service1', [])

        router.add_service(service1)

        self.assertEqual(len(router.services), 1)
        self.assertEqual(router.services[service1.name], service1)

    def test_add_service_already_registered(self):
        router = ServicesRouter('path')
        service1 = Service('service1', [])

        router.add_service(service1)

        with self.assertRaises(ValueError):
            router.add_service(service1)

    def test_get_service(self):
        router = ServicesRouter('path')
        service1 = Service('service1', [])

        router.add_service(service1)
        service1_get = router.get_service(service1.name)
        self.assertEqual(service1, service1_get)

    def test_get_service_unregistered(self):
        router = ServicesRouter('path')

        with self.assertRaises(ValueError):
            router.get_service('unregistered_service')

    def test_remove_service(self):
        service1 = Service('service1', [])
        router = ServicesRouter('path', [service1])

        router.remove_service(service1.name)
        self.assertEqual(len(router.services), 0)

    def test_remove_service_unregistered(self):
        router = ServicesRouter('path')

        with self.assertRaises(ValueError):
            router.remove_service('unregistered_service')
