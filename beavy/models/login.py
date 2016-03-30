from flask_babel import gettext as _
from werkzeug.exceptions import BadRequest
from sqlalchemy import orm, func
from ..app import db, app
from .persona import Persona, Role
from .profile import Profile
from kombu.utils import cached_property

import logging
import datetime


class ProxyProperty(object):

    def __init__(self, attr, target="persona"):
        self.attr = attr
        self.target = target

    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.target), self.attr)

    def __set__(self, obj, value):
        setattr(getattr(obj, self.target), self.attr, value)


class Login(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column('created_at', db.DateTime(),
                           nullable=False, server_default=func.now())
    persona_id = db.Column(db.Integer, db.ForeignKey('persona.id'),
                           nullable=False)
    persona = orm.relationship(Persona, foreign_keys=persona_id,
                               backref=orm.backref('logins', order_by=id))

    # any of the social providers,
    # or local email-addr+password login
    provider = db.Column(db.String(255), nullable=False)
    profile_id = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    access_token = db.Column(db.String(255))
    secret = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    cn = db.Column(db.String(255))
    profile_url = db.Column(db.String(512))
    image_url = db.Column(db.String(512))

    #
    #
    #
    #
    # Next up: stay compatible with Flask-Security

    is_authenticated = True
    is_anonymous = False

    # we proxy those over from the underlying persona
    active = ProxyProperty("active")
    confirmed_at = ProxyProperty("confirmed_at")
    last_login_at = ProxyProperty("last_login_at")
    current_login_at = ProxyProperty("current_login_at")
    last_login_ip = ProxyProperty("last_login_ip")
    current_login_ip = ProxyProperty("current_login_ip")
    login_count = ProxyProperty("login_count")
    language_preference = ProxyProperty("language_preference")

    def get_user(self):
        return self.persona

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return self.active

    @property
    def password(self):
        return self.access_token if self.provider == "email" else None

    @cached_property
    def roles(self):
        # Should this go to "current_persona"?
        from beavy.app import app
        system_role = Role.query.filter_by(source_id=self.persona.id,
                                           target_id=app.system_persona_id
                                           ).first()
        if system_role:
            return [system_role]
        return []

    @property
    def is_staff(self):
        return self.roles != []
    #
    # ------------------------ END FLASK SECURITY --------------------
    #
    #
    #
    # Next: Flask-Social-Blueprint compatiblity layer

    @classmethod
    def by_profile(cls, profile):
        provider = profile.data["provider"]
        return cls.query.filter(cls.provider == provider,
                                cls.profile_id == profile.id).first()

    @classmethod
    def from_profile(cls, persona, profile):
        if not persona or persona.is_anonymous:
            if not app.config.get("SECURITY_REGISTERABLE"):
                msg = "Persona not found. Registration disabled."
                logging.warning(msg)
                raise Exception(_(msg))
            email = profile.data.get("email")
            if not email:
                msg = "Please provide an email address."
                logging.warning(msg)
                raise Exception(_(msg))
            found = Login.query.filter(Login.email == email).first()
            if found:
                persona = found.persona
            else:

                now = datetime.now()
                persona = Profile(
                    pretty_name="{} {}".format(profile.data.get("first_name"),
                                               profile.data.get("last_name")),
                    confirmed_at=now,
                    active=True)

                db.session.add(persona)
                db.session.flush()

        assert persona.id, "Persona does not have an id"
        login = cls(persona_id=persona.id, **profile.data)
        db.session.add(login)
        db.session.commit()
        return login

    #
    # ------------------------ END FLASK SOCIAL BLUEPRINT --------------------
    #
    #
    #
    # Next: Our own adaptions to use the social blueprints style system

    @classmethod
    def with_password(cls, username, password):
        return cls.query.filter(cls.provider == "email",
                                cls.profile_id == username,
                                cls.access_token == password).first()

    @classmethod
    def with_one_time_token(cls, token):
        return cls.query.filter(cls.provider == "onetimetoken",
                                cls.access_token == token).first()

    @cached_property
    def current_persona(self):
        from beavy.app import app, request

        requested_idenity = request.headers.get("X-Act-As-Identity", None)
        if not requested_idenity:
            return self.persona

        for persona in self.persona.personas:
            if requested_idenity == persona.id or \
               requested_idenity == persona.name:
                # Should we check the "roles" here?
                return persona

        else:
            raise BadRequest("You are asking to act as an entity you can't access.")
