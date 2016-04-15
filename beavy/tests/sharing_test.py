from beavy.app import app, db
from beavy.models.persona import Persona, Role, Profile, Organisation
from beavy.models.object import Object
from beavy.models.activity import Shared, Unshared
from werkzeug.exceptions import BadRequest
from beavy.models.login import Login
from beavy.utils.db_helpers import set_db_persona

from sqlalchemy.exc import ProgrammingError as SQLProgrammingError

import pytest


class TestObject(Object):
    __mapper_args__ = {
        'polymorphic_identity': "test"
    }


def _gen_people(db_session):
    login = Login(provider="test", profile_id="me", persona=Profile())
    other = Login(provider="test", profile_id="other", persona=Profile() )
    obj = TestObject(owner=login.persona)
    db_session.add(login)
    db_session.add(other)
    db_session.add(obj)
    db_session.commit()
    return (login, other, obj)


@pytest.yield_fixture(scope='function')
def logged_in_session(testapp, db_session):
    login, other, obj = _gen_people(db_session)
    with testapp.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = login.id
            sess['_fresh'] = True
        yield (c, login, other, obj)


def test_simple_sharing(testapp, logged_in_session, db_session):
    client, login, other, obj = logged_in_session


    with testapp.test_request_context() as t:
        set_db_persona(login.persona)
        t.user = login
        # share the object
        obj.share_with(other.persona)
        db_session.commit()
        # we should find five publicly accessiable objects
        # and see none of the private from other person ones
        t.user = other
        assert Object.query.accessible.count() == 1
        assert Object.query.accessible.first().id == obj.id
        #
        shared = Shared.query.first()
        assert shared is not None, "Sharing Wasn't properly logged"
        assert shared.subject_id == login.current_persona.id
        assert shared.whom_id == other.persona.id
        assert shared.object_id == obj.id
        # assert shared.payload == {"level": "view"}

        # change the share level
        t.user = login
        obj.share_with(other.persona, level="admin")
        db_session.commit()

        t.user = other
        assert Object.query.accessible.count() == 1
        assert Object.query.accessible.first().id == obj.id

        assert Shared.query.count() == 2
        assert Unshared.query.count() == 1

        shared = Shared.query[1]
        assert shared is not None, "Sharing Wasn't properly logged"
        assert shared.subject_id == login.current_persona.id
        assert shared.whom_id == other.persona.id
        assert shared.object_id == obj.id
        # assert shared.payload == {"level": "admin"}

        unshared = Unshared.query.first()
        assert unshared is not None, "Sharing Wasn't properly logged"
        assert unshared.subject_id == login.current_persona.id
        assert unshared.whom_id == other.persona.id
        assert unshared.object_id == obj.id
        # assert unshared.payload == {"level": "admin"}


        # not actually change the share level
        t.user = login
        obj.share_with(other.persona, level="admin")
        db_session.commit()

        t.user = other
        assert Object.query.accessible.count() == 1
        assert Object.query.accessible.first().id == obj.id

        # no logging happens
        assert Shared.query.count() == 2
        assert Unshared.query.count() == 1


def test_sharing_without_db_persona_fails_on_db(testapp, logged_in_session, db_session):
    client, login, other, obj = logged_in_session

    with testapp.test_request_context() as t:
        t.user = login
        # share the object
        with pytest.raises(SQLProgrammingError):
            obj.share_with(other.persona)
            db_session.commit()

        # make sure the sharing was prevented
        db_session.rollback()

        assert Object.query.count() == 1
        assert Shared.query.count() == 0
