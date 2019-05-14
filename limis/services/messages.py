"""
limis services - messages

Messages used for logging and exception handling.
"""
COMPONENT_ACTION_NOT_IMPLEMENTED_ERROR = '"{}" action is not implemented for this service.'
COMPONENT_INIT_NOT_PROPERLY_CONFIGURED_ERROR = '"{}" is not properly configured. Attribute "{}" is not type "{}".'
ROUTER_ADD_SERVICE = 'Adding "{}" service.'
ROUTER_ADD_SERVICE_ALREADY_REGISTERED = '"{}" service is already registered.'
ROUTER_BUILD_ROUTER_RULES = 'Building router rules.'
ROUTER_BUILD_ROUTER_RULES_ADD_SERVICE = 'Adding service router rule "{}" with path "{}" to services router.'
ROUTER_BUILD_ROUTERS = 'Building routers.'
ROUTER_GET_REMOVE_SERVICE_NOT_REGISTERED = '"{}" service is not registered.'
ROUTER_GET_SERVICE = 'Retrieving "{}" service.'
ROUTER_REMOVE_SERVICE = 'Removing "{}" service.'
RESOURCE_DESERIALIZE_OBJECT_TYPE_MISMATCH = '"{}" attribute has type "{}" which does not match the object type "{}".'
RESOURCE_DESERIALIZE_OBJECT_MISSING_ATTRIBUTE = '"{}" does not have attribute "{}" defined.'
RESOURCE_DESERIALIZE_INVALID_DATA_TYPE = 'Data must be a JSON object.'
RESOURCE_SERIALIZE_UNKNOWN_ATTRIBUTE = 'Attribute "{}" is not present in class "{}".'
SERVICE_ADD_COMPONENT = 'Service "{}" registering component "{}" with path "{}".'
SERVICE_ADD_COMPONENT_INVALID_COMPONENT_CLASS = 'Component "{}" is not a subclass of Component class.'
SERVICE_ADD_COMPONENT_INVALID_COMPONENT_TYPE = 'Component is not a class.'
SERVICE_ADD_COMPONENT_REGISTER_HANDLER = 'Service "{}" registering component "{}" handler "{}".'
SERVICE_ADD_COMPONENT_WITH_NO_HANDLER = 'Component "{}" has been registered with the Service "{}" but \
does not have any handlers defined.'
SERVICE_INIT_REGISTER_COMPONENTS_STARTED = 'Service "{}" registering components.'
SERVICE_INIT_REGISTER_COMPONENTS_COMPLETED = 'Service "{}" registered components.'
