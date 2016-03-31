from flask_script import Manager
from flask.ext.security.utils import encrypt_password

from beavy.models.login import Login
from beavy.models.persona import Role
from beavy.models.profile import Profile
from beavy.app import app, db

from datetime import datetime
from random import sample, choice

import string


CHARS = string.ascii_letters + string.digits
LENGTH = 10


UserCommand = Manager(usage="manage user objects")


@UserCommand.command
def create(email, password=None, **persona_info):

    if password:
        pw = password
    else:
        pw = ''.join(choice(CHARS) for _ in range(LENGTH))

    if db.session.query(Login).filter_by(provider="email",
                                         profile_id=email).first():
        print("User Login already existing for {}".format(email))
        exit(1)

    db.session.add(Login(provider="email",
                         profile_id=email,
                         access_token=encrypt_password(pw),
                         persona=Profile(active=True,
                                         confirmed_at=datetime.now(),
                                         **persona_info)))
    db.session.commit()

    if password:
        print("Profile and Login created for {}".format(email))
    else:
        print("Profile and Login for {} created with password: {} ".format(
              email, pw))


@UserCommand.command
def activate(email):
    login = db.session.query(Login).filter_by(provider="email",
                                              profile_id=email).first()
    if not login:
        print("Login not found!")
        exit(1)

    login.persona.active = True
    if not login.persona.confirmed_at:
        login.persona.confirmed_at = datetime.now()

    db.session.add(login.persona)
    db.session.commit()

    print("Login/Persona {} activated".format(email))


@UserCommand.command
def deactivate(email):
    login = db.session.query(Login).filter_by(provider="email",
                                              profile_id=email).first()
    if not login:
        print("Login not found!")
        exit(1)

    login.persona.active = False
    db.session.add(login.persona)
    db.session.commit()

    print("Login/Persona {} deactivated".format(email))


@UserCommand.command
@UserCommand.option("", dest="role", default="moderator",
                    help="The role you want that person to have")
def promote(email, role='moderator'):
    login = db.session.query(Login).filter_by(provider="email",
                                              profile_id=email).first()
    if not login:
        print("Login not found!")
        exit(1)

    persona = login.persona
    system = app.system_persona
    rl = db.session.query(Role).filter_by(source_id=persona.id,
                                          target_id=system.id).first()
    if rl:
        rl.role = role
        db.session.add(rl)
        msg = "Updated {} role to '{}'".format(email, role)
    else:
        db.session.add(Role(source_id=persona.id,
                            target_id=system.id,
                            role=role))
        msg = "Added {} to staff with role {}".format(email, role)

    db.session.commit()
    print(msg)


@UserCommand.command
def demote(email):
    login = db.session.query(Login).filter_by(provider="email",
                                              profile_id=email).first()
    if not login:
        print("Login not found!")
        exit(1)

    persona = login.persona
    system = app.system_persona
    rl = db.session.query(Role).filter_by(source_id=persona.id,
                                          target_id=system.id).first()
    if rl:
        db.session.delete(rl)
        db.session.commit()
        print("Removed {} from system roles".format(email))
    else:
        print("{} doesn't have any system roles".format(email))
