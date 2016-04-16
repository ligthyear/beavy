from .object import Object
from urllib.parse import urlparse
from sqlalchemy import event


class External(Object):
    """
    This Object represents something linked to outside of our system
    """
    __mapper_args__ = {
        'polymorphic_identity': "external"
    }


def ensure_link(mapper, connection, target):
    try:
        urlparse(target.payload['link'])
    except (KeyError, TypeError, AttributeError):
        raise ValueError("Payload.link isn't a proper URL")

event.listen(External, 'before_insert', ensure_link)
event.listen(External, 'before_update', ensure_link)
