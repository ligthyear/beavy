from .activity import Activity
from sqlalchemy.orm import validates


class Mentioned(Activity):
    """
    This Activity represents an someone being mentioned
    """
    __mapper_args__ = {
        'polymorphic_identity': "mentioned"
    }

    @validates('object_id', 'whom_id')
    def ensure_parties(self, key, value):
        """
        A mention _must have_ object_id and whom_id, otherwise
        it becomes inconsistent
        """
        assert value is not None, "{} can't be None".format(key)
        return value
