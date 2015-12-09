from mixer.backend.flask import mixer
from flask.ext.security.utils import encrypt_password
from datetime import datetime
from beavy.app import db


def to_dict(mdl):
    return dict((column_name, getattr(mdl, column_name))
                for column_name in mdl.__table__.c.keys())


def generate_new_persona(**kwargs):
    # make sure, newly created persona isn't existing any longer
    user = mixer.blend('beavy.models.user.User', **kwargs)
    db.session.delete(user)
    db.session.commit()
    return to_dict(user)


def ensure_personas():
    return {
        'malcolm': to_dict(mixer.blend('beavy.models.user.User',
                                       name="Malcolm Reynolds",
                                       password=encrypt_password('password'),
                                       active=True,
                                       confirmed_at=datetime.now())),
        'zoe':  to_dict(mixer.blend('beavy.models.user.User',
                                    name="Zoe Washburne",
                                    password=encrypt_password('password'),
                                    active=True,
                                    confirmed_at=datetime.now())),
        'inara': to_dict(mixer.blend('beavy.models.user.User',
                                     name="Inara Serra",
                                     password=encrypt_password('password'),
                                     active=True,
                                     confirmed_at=datetime.now()))
    }
