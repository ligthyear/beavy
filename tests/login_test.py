from beavy.app import app, db, current_user
from beavy.models.persona import Persona, Role, Profile, Organisation 
from werkzeug.exceptions import BadRequest
from beavy.models.login import Login
from flask.ext.security.utils import encrypt_password
from datetime import datetime

import pytest

def test_simple_login(db_session, testapp):
    l = Login(provider="email",
              profile_id="test@example.com",
              access_token=encrypt_password("1234567890-test"),
              persona=Profile(active=True, confirmed_at=datetime.now()))

    db_session.add(l)
    db_session.commit()

    with testapp.test_client() as client:
        resp = client.post('/login',
                           data={
                            "email": "test@example.com",
                            "password":"1234567890-test"})

        assert current_user == l, "Login Failed"


def test_ensure_inactive(db_session, testapp):
    l = Login(provider="email",
              profile_id="test@example.com",
              access_token=encrypt_password("1234567890-test"),
              persona=Profile(active=False, confirmed_at=datetime.now()))

    db_session.add(l)
    db_session.commit()

    with testapp.test_client() as client:
        resp = client.post('/login',
                           data={
                            "email": "test@example.com",
                            "password":"1234567890-test"})

        assert current_user != l, "Login succeed but shouldn't"
        assert "Confirm account" in str(resp.data)


def test_ensure_unconfirmed(db_session, testapp):
    l = Login(provider="email",
              profile_id="test@example.com",
              access_token=encrypt_password("1234567890-test"),
              persona=Profile(active=True))

    db_session.add(l)
    db_session.commit()

    with testapp.test_client() as client:
        resp = client.post('/login',
                           data={
                            "email": "test@example.com",
                            "password":"1234567890-test"})

        assert current_user != l, "Login succeed but shouldn't"
        assert "Confirm account" in str(resp.data)
