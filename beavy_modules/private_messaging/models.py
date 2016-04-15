from beavy.models.object import Object
from beavy.common.payload_property import PayloadProperty
from beavy.utils.url_converters import ModelConverter

PM_ID = "private_message"


class PrivateMessage(Object):
    __mapper_args__ = {
        'polymorphic_identity': PM_ID
    }

    title = PayloadProperty('title')


ModelConverter.__OBJECTS__['private_message'] = PrivateMessage
