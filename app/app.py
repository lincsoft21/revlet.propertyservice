from propertyservice_client import RevletPropertyService

PROPERTYSERVICE_CLIENT = RevletPropertyService()


def get_properties(event, context):
    return PROPERTYSERVICE_CLIENT.get_properties(event, context)


def post_property(event, context):
    return PROPERTYSERVICE_CLIENT.post_property(event, context)


def update_property_details(event, context):
    return PROPERTYSERVICE_CLIENT.update_property_details(event, context)


def delete_property(event, context):
    return PROPERTYSERVICE_CLIENT.delete_property(event, context)
