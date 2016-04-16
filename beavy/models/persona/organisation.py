from .persona import Persona


class Organisation(Persona):
    """
    This persona represent an organisation, a group of actors which act as one
    entity
    """
    __mapper_args__ = {
        'polymorphic_identity': "organisation"
    }
