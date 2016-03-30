from .persona import Persona


class Person(Persona):
    """
    This persona represent a real human actor – a natural person.
    """
    __mapper_args__ = {
        'polymorphic_identity': "person"
    }
