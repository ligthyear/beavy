from beavy.app import app, db
from beavy.models.persona import Persona, Role
from beavy.models.profile import Profile
from beavy.models.object import Object
from beavy.models.organisation import Organisation
from werkzeug.exceptions import BadRequest
from beavy.models.login import Login

import pytest

class TestObject(Object):
    __mapper_args__ = {
        'polymorphic_identity': "test"
    }


def _gen_owner(db_session):
    group = Organisation(id=1999, name="test_group")

    # no membership
    groupie = Login(provider="test", profile_id="normal", persona=Profile())
    db_session.add(group)
    db_session.add(groupie)

    db_session.commit()

    db_session.add(Role(source_id=groupie.persona_id,
                        target_id=group.id,
                        role="member"))

    obj = TestObject(owner=groupie.persona, public=False)
    db_session.add(obj)
    db_session.commit()
    return (groupie, group, obj)


def test_persona_no_object_access(testapp, db_session):
    member, group, obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.add(TestObject(owner=other.persona, public=False))
    db_session.commit()

    with testapp.test_request_context():
        # without any user context, we shouldn't find any thing
        assert Object.query.accessible.count() == 0


def test_no_persona_public_object_access(testapp, db_session):
    # someone
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.add(TestObject(owner=other.persona, public=True))
    db_session.commit()

    with testapp.test_request_context():
        # without any user context, we shouldn't find any thing
        assert Object.query.accessible.count() == 1

def test_persona_object_access(testapp, db_session):
    member, group, obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.add(TestObject(owner=other.persona, public=False))
    db_session.commit()

    with testapp.test_request_context() as t:
        t.user = member
        # we should find _one_ accessible object
        assert Object.query.accessible.count() == 1


def test_parent_persona_object_access(testapp, db_session):
    member, group, obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.add(TestObject(owner=other.persona, public=False))
    db_session.commit()

    db_session.add(TestObject(owner=group, public=False))
    db_session.commit()

    with testapp.test_request_context() as t:
        t.user = member
        # we should find two accessible objects
        # one from the user, one from the group
        assert Object.query.accessible.count() == 2

# THIS isn't properly implemented yet, hence a failing test
# we know about.
@pytest.mark.xfail(raises=AssertionError)
def test_parent_persona_super_object_access(testapp, db_session):
    member, group, top_obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.add(TestObject(owner=other.persona, public=True, belongs_to_id=top_obj.id))
    db_session.commit()

    with testapp.test_request_context() as t:
        t.user = member
        # we should find two accessible objects
        # one from the user, one from the group
        assert Object.query.accessible.count() == 2
