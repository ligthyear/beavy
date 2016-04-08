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
    group = Organisation()

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



def test_grand_parent_persona_object_access(testapp, db_session):
    # building a complex persona tree:
    grand, _, _ = _gen_owner(db_session)
    dad, _, _ = _gen_owner(db_session)
    kid, _, _ = _gen_owner(db_session)


    # kid can access everything dad can access
    db_session.add(Role(source_id=kid.persona.id,
                        target_id=dad.persona.id,
                        role="member"))

    # and dad can access everything grand can access
    db_session.add(Role(source_id=dad.persona.id,
                        target_id=grand.persona.id,
                        role="member"))

    db_session.commit()


    with testapp.test_request_context() as t:
        t.user = grand
        # grand does only have his level
        assert Object.query.accessible.count() == 1

    with testapp.test_request_context() as t:
        t.user = dad
        # dad has a level more
        assert Object.query.accessible.count() == 2

    with testapp.test_request_context() as t:
        t.user = kid
        # kid has three levels of access
        assert Object.query.accessible.count() == 3

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
