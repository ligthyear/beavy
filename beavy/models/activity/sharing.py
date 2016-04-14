from ..activity import Activity


class Shared(Activity):
    """
    This Activity represents an object having been shared with
    someone else
    """
    __mapper_args__ = {
        'polymorphic_identity': "shared"
    }


class Unshared(Activity):
    """
    This Activity represents a share having been removed for
    a third party
    """
    __mapper_args__ = {
        'polymorphic_identity': "unshared"
    }
