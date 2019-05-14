"""
limis service - components

Service components, abstract Component class provides base functionality. Resource driven approach included with
Resource class.
"""
import inspect
import json
import logging

from abc import ABC
from typing import Any, Callable, Dict, List, Tuple, TypeVar

from limis.core import settings
from limis.services import messages

int_or_string = TypeVar('int_or_string', int, str)
dict_or_list = TypeVar('dict_or_list', Dict[Any, Any], List[Any])


def action(func) -> Callable:
    """
    Decorator to add the '__action__' attribute to component actions that are callable.

    :param func: Function to decorate.
    :return: Function with attribute.
    """
    func.__action__ = True
    return func


class Component(ABC):
    """
    Abstract Base component class to be extended by service component types. Core service component types are:

        * :class:`.Resource`

    :attribute component_name: The name of the component.
    :attribute component_path: The path of the component.
    :attribute component_http_handler: The HTTP handler for the component.
    :attribute component_websocket_handler: The WebSocket handler for the component.
    :attribute exclude_attributes: Class attribute of excluded attributes for serialization, this should be set in your
      inherited class.
    :attribute system_exclude_attributes: Class attribute of system excluded attributes for serialization, this should
      generally not be set by your inherited class.

    The 'component_name' and '_component_path' attributes must be set by your inherited component.
    """
    component_name = None
    component_path = None
    component_http_handler = None
    component_websocket_handler = None

    exclude_attributes = []
    system_exclude_attributes = [
        'component_name', 'component_path',
        'component_http_handler', 'component_websocket_handler',
        'logger'
    ]

    def __init__(self):
        """
        Initializes Component class.

        :raises ValueError: Error indicating the component is not properly configured.
        """
        self.logger = logging.getLogger(__name__)
        if not isinstance(self.component_name, str):
            msg = messages.COMPONENT_INIT_NOT_PROPERLY_CONFIGURED_ERROR.format(
                self.__class__.__name__, 'component_name', 'str')

            self.logger.error(msg)
            raise ValueError(msg)

        if not isinstance(self.component_path, str):
            msg = messages.COMPONENT_INIT_NOT_PROPERLY_CONFIGURED_ERROR.format(
                self.__class__.__name__, 'component_path', 'str')

            self.logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def _get_method_name():
        """
        Inspects the stack to determine the method name.

        :return: Returns the method name from which this was called.
        """
        return inspect.stack()[1][3]

    @classmethod
    def _render_json(cls, data: Any, default: Any = None,
                     indent: int = -1, separators: Tuple[str, str] = -1, sort_keys: bool = None) -> str:
        """
        Renders a data object to json using the provided settings if set, otherwise the system configured defaults will
        be used. Settings that are used to configure the defaults are:

        * json['indent']
        * json['separator_item']
        * json['separator_key']
        * json['sort_keys']

        :param data: Data to dump to JSON
        :param default: JSON encoder function
        :param indent: JSON indent size
        :param separators: JSON Item and Key separators
        :param sort_keys: Flag to sort keys in JSON string
        :return: JSON string
        """
        default_indent = settings.json['indent'] if settings.json['indent'] != '' else None
        default_separators = (settings.json['separator_item'], settings.json['separator_key'])
        default_sort_keys = bool(settings.json['sort_keys'])

        indent = default_indent if indent == -1 else indent
        separators = default_separators if separators == -1 else separators
        sort_keys = default_sort_keys if sort_keys is None else sort_keys

        return json.dumps(data, default=default, indent=indent, separators=separators, sort_keys=sort_keys)

    @classmethod
    def actions(cls) -> List[str]:
        """
        Generates a list of actions as defined by the component.

        :return: List of component actions.
        """
        actions = []

        for key in dir(cls):
            value = getattr(cls, key)

            try:
                is_action = value.__action__
            except AttributeError:
                is_action = False

            if is_action:
                actions.append(value.__name__)

        return actions

    @classmethod
    def attributes(cls) -> List[str]:
        """
        Generates a list of attributes defined by the component.

        The following attributes are excluded:

        * Private attributes starting with at '_'
        * Callable attributes
        * Class methods
        * Attributes listed in exclude_attributes or system_exclude_attributes.

        :return: List of component attributes.
        """
        attributes = []

        for key, value in cls.__dict__.items():
            if not key.startswith('_') and not callable(value) and not type(value).__name__ == 'classmethod' and \
               not key == 'exclude_attributes' and not key == 'system_exclude_attributes' and \
               key not in cls.exclude_attributes and key not in cls.system_exclude_attributes:
                attributes.append(key)

        return attributes

    @classmethod
    @action
    def define(cls, indent: int = -1, separators: Tuple[str, str] = -1, sort_keys: bool = None) -> str:
        """
        Defines the current component and returns a JSON formatted string with the class definition.

        :param indent: If not None JSON data will be pretty-printed with the specified ident level.
        :param separators: Tuple representing the item and key separators.
        :param sort_keys: Bool value determines if dictionary keys will be sorted.
        :return definition: String representing the component definition in JSON format.
        """
        attributes = cls.attributes()
        actions = cls.actions()

        data = {
            'name': cls.component_name,
            'attributes': attributes,
            'actions': actions
        }

        return cls._render_json(data, indent=indent, separators=separators, sort_keys=sort_keys)


class Resource(Component):
    """
    Resource
    """
    @action
    def create(self):
        """
        Optional abstract method to be implemented with functionality to create a resource.

        :raises NotImplementedError: Error indicating this action has not been implemented by the component.
        """
        msg = messages.COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR.format(self.__class__._get_method_name())

        self.logger.error(msg)
        raise NotImplementedError(msg)

    @action
    def delete(self):
        """
        Optional abstract method to be implemented with functionality to delete a resource.

        :raises NotImplementedError: Error indicating this action has not been implemented by the component.
        """
        msg = messages.COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR.format(self.__class__._get_method_name())

        self.logger.error(msg)
        raise NotImplementedError(msg)

    @classmethod
    @action
    def find(cls):
        """
        Optional bstract class method to be implemented with functionality to find a set of resources based on criteria.

        :raises NotImplementedError: Error indicating this action has not been implemented by the component.
        """
        msg = messages.COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR.format(cls._get_method_name())

        logging.getLogger(__name__).error(msg)
        raise NotImplementedError(msg)

    @classmethod
    @action
    def get(cls, identifier: int_or_string) -> str:
        """
        Abstract class method to be implemented with functionality to get a resource by a unique identifier.
        Implementors should retrieve resource data from the back-end and render it as a JSON object per the applications
        specifications.

        :param identifier: A unique resource identifier that may be either a string or integer.
        :return: JSON string representing the resource.

        :raises NotImplementedError: Error indicating this action has not been implemented by the component.
        """
        msg = messages.COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR.format(cls._get_method_name())

        logging.getLogger(__name__).error(msg)
        raise NotImplementedError(msg)

    @action
    def update(self):
        """
        Abstract method to be implemented with functionality to update a resource.

        :raises NotImplementedError: Error indicating this action has not been implemented by the component.
        """
        msg = messages.COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR.format(self.__class__._get_method_name())

        self.logger.error(msg)
        raise NotImplementedError(msg)

    def deserialize(self, data: str, strict: bool = True):
        """
        Deserializes a JSON string into an object, if strict is enabled the method will fail if the class does not have
        an attribute defined.

        :param data: JSON string to process.
        :param strict: Flat go enable strict mode, default is True
        :raises TypeError: Error indicating the input data is invalid.
        :raises ValueError: Error indicating the class missing an attribute defined in the input.
        """
        try:
            data_dict = json.loads(data)
        except TypeError:
            self.logger.error(messages.RESOURCE_DESERIALIZE_INVALID_DATA_TYPE)
            raise TypeError(messages.RESOURCE_DESERIALIZE_INVALID_DATA_TYPE)

        for key in data_dict:
            value = data_dict[key]

            if strict:
                if not hasattr(self, key):
                    msg = messages.RESOURCE_DESERIALIZE_OBJECT_MISSING_ATTRIBUTE.format(
                        self.__class__.__name__, key)

                    self.logger.error(msg)
                    raise ValueError(msg)

                data_attribute_type = type(value).__name__
                object_attribute_type = type(getattr(self, key)).__name__

                if object_attribute_type != data_attribute_type:
                    msg = messages.RESOURCE_DESERIALIZE_OBJECT_TYPE_MISMATCH.format(
                        key, data_attribute_type, object_attribute_type)

                    self.logger.error(msg)
                    raise ValueError(msg)

            setattr(self, key, value)

    def serialize(self, exclude_attributes: List[str] = [],
                  indent: int = -1, separators: Tuple[str, str] = -1, sort_keys: bool = None) -> str:
        """
        Serializes the current object into a JSON string.

        Class attribute 'exclude_attributes' is a list of class instance attribute names that will always be excluded
        from the serialization. In addition the method variable 'exclude_attributes' can be specified on a per call
        basis to exclude additional attributes not defined at the class level.

        :param exclude_attributes: List of attribute names to exclude from serialization.
        :param indent: If not None JSON data will be pretty-printed with the specified ident level.
        :param separators: Tuple representing the item and key separators.
        :param sort_keys: Bool value determines if dictionary keys will be sorted.
        :return resource: String representing serialized object in JSON format.
        """
        exclude_attributes = \
            self.__class__.system_exclude_attributes + self.__class__.exclude_attributes + exclude_attributes

        attributes = {}

        for attribute in self.attributes():
            if attribute not in exclude_attributes:
                attributes[attribute] = getattr(self, attribute)

        resource = self._render_json(attributes, indent=indent, separators=separators, sort_keys=sort_keys)

        return resource
