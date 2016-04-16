from .activity import Activity
from sqlalchemy.orm import validates


class Visited(Activity):
    """
    This Activity represents an someone being mentioned
    """
    __mapper_args__ = {
        'polymorphic_identity': "visited"
    }

    @validates('object_id')
    def ensure_parties(self, key, value):
        """
        A mention _must have_ object_id
        """
        assert value is not None, "{} can't be None".format(key)
        return value
