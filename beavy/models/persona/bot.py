from .persona import Persona


class Bot(Persona):
    """
    This persona represent an automatic actor – like a bot or automatic
    process.
    """
    __mapper_args__ = {
        'polymorphic_identity': "bot"
    }
