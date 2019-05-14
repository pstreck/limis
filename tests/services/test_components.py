import json
import logging

from unittest import TestCase

from limis.services.components import action, Component, Resource


class TestComponent(TestCase):
    class TestComponent(Component):
        component_name = 'test_component'
        component_path = 'test_component'
        test_attribute = 'test_attribute'

        @classmethod
        @action
        def test_action(cls):
            return 'test action'

    def test_init(self):
        component = TestComponent()

    def test_init_improperly_configured_component_name(self):
        class ImproperlyConfiguredComponent(Component):
            component_path = 'test_component'

        with self.assertRaises(ValueError):
            component = ImproperlyConfiguredComponent()

    def test_init_improperly_configured_component_path(self):
        class ImproperlyConfiguredComponent(Component):
            component_name = 'test_component'

        with self.assertRaises(ValueError):
            component = ImproperlyConfiguredComponent()

    def test__get_method_name(self):
        self.assertEqual(Component._get_method_name(), 'test__get_method_name')

    def test_actions_base(self):
        self.assertEqual(Component.actions(), ['define'])

    def test_actions_extended(self):
        self.assertEqual(self.TestComponent.test_action(), 'test action')
        self.assertEqual(self.TestComponent.actions(), ['define', 'test_action'])

    def test_attributes_base(self):
        self.assertEqual(Component.attributes(), [])

    def test_attributes_extended(self):
        self.assertEqual(self.TestComponent.attributes(), ['test_attribute'])

    def test_define_base(self):
        data = {
            'name': Component.component_name,
            'actions': Component.actions(),
            'attributes': Component.attributes()
        }

        self.assertEqual(Component.define(), Component._render_json(data))

    def test_define_extended(self):
        data = {
            'name': self.TestComponent.component_name,
            'actions': self.TestComponent.actions(),
            'attributes': self.TestComponent.attributes()
        }

        self.assertEqual(self.TestComponent.define(), self.TestComponent._render_json(data))


class TestResource(TestCase):
    class TestResource(Resource):
        component_name = 'test_resource'
        component_path = 'test_resource'
        test_attribute = 'test attribute'

    class TestResourceAdditionalAttribute(Resource):
        component_name = 'test_resource'
        component_path = 'test_resource'
        test_attribute = 'test attribute 1'
        test_attribute2 = 'test attribute 2'

    def setUp(self):
        logging.getLogger('limis.services.components').disabled = True

    def tearDown(self):
        logging.getLogger('limis.services.components').disabled = False

    def test_create(self):
        resource = self.TestResource()

        with self.assertRaises(NotImplementedError):
            resource.create()

    def test_delete(self):
        resource = self.TestResource()

        with self.assertRaises(NotImplementedError):
            resource.delete()

    def test_find(self):
        with self.assertRaises(NotImplementedError):
            self.TestResource.find()

    def test_get(self):
        with self.assertRaises(NotImplementedError):
            self.TestResource.get(None)

    def test_update(self):
        resource = self.TestResource()

        with self.assertRaises(NotImplementedError):
            resource.update()

    def test_deserialize_valid_strict(self):
        resource_to_serialize = self.TestResource()
        data = resource_to_serialize.serialize()

        resource_to_deserialize = self.TestResource()
        resource_to_deserialize.deserialize(data)

        self.assertEqual(resource_to_serialize.test_attribute, resource_to_deserialize.test_attribute)

        with self.assertRaises(TypeError):
            resource_to_deserialize.deserialize(0)

        resource_to_serialize = self.TestResourceAdditionalAttribute()

        data = resource_to_serialize.serialize()

        resource_to_deserialize = self.TestResource()
        with self.assertRaises(ValueError):
            resource_to_deserialize.deserialize(data)

        resource_to_serialize = self.TestResource()
        resource_to_serialize.test_attribute = 0

        data = resource_to_serialize.serialize()

        resource_to_deserialize = self.TestResource()
        with self.assertRaises(ValueError):
            resource_to_deserialize.deserialize(data)

    def test_deserialize_valid_not_strict(self):
        resource_to_serialize = self.TestResourceAdditionalAttribute()

        data = resource_to_serialize.serialize()

        resource_to_deserialize = self.TestResource()
        resource_to_deserialize.deserialize(data, strict=False)

        self.assertEqual(resource_to_serialize.test_attribute, resource_to_deserialize.test_attribute)

    def test_serialize(self):
        resource = self.TestResource()
        json_data = resource.serialize()
        obj_data = json.loads(json_data)

        self.assertEqual(obj_data['test_attribute'], self.TestResource.test_attribute)
