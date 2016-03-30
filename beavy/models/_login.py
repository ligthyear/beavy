from flask.ext.security import UserMixin
from flask_security.forms import ConfirmRegisterForm, RegisterForm, StringField
from sqlalchemy import func
from beavy.app import db
from .persona import Persona


RegisterForm.name = StringField('Full Name')
ConfirmRegisterForm.name = StringField('Full Name')


class Login(db.Model, UserMixin):
    __LOOKUP_ATTRS__ = []

    discriminator = db.Column('type', db.String(100), nullable=False)

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column('created_at', db.DateTime(), nullable=False,
                           server_default=func.now())
    name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())

    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(255))
    current_login_ip = db.Column(db.String(255))
    login_count = db.Column(db.Integer())
    language_preference = db.Column(db.String(2))

    personas = db.relationship('Persona', secondary="user_personas")
    primary_persona = db.Column(db.Integer,
                                db.ForeignKey(Persona.id),
                                nullable=False)
