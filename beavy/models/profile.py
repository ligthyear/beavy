from flask.ext.security import UserMixin
from .person import Person
from beavy.app import db


class Profile(Person, UserMixin):
    """
    This persona represent a real human actor – a natural person.
    """
    __mapper_args__ = {
        'polymorphic_identity': "profile"
    }

    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer())
    language_preference = db.Column(db.String(2))

    # personas = db.relationship('Persona', secondary=Role,
    #     primaryjoin=Person.id==Role.c.profile_id,
    #     secondaryjoin=Person.id==Role.c.profile_id)
