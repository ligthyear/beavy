from .object import Object
from sqlalchemy.orm import validates


class External(Object):
    """
    This Object represents something linked to outside of our system
    """
    __mapper_args__ = {
        'polymorphic_identity': "external"
    }

    @validates('payload')
    def ensure_link(self, key, value):
        """
        Make sure we are having a link in the payload
        """
        assert value["link"]
        return value
