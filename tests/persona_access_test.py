from beavy.app import app, db
from beavy.models.persona import Persona, Role
from beavy.models.profile import Profile
from beavy.models.object import Object, SharedWith
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
        # one from the user, one through the access point
        assert Object.query.accessible.count() == 2


def test_parent_persona_super_object_tree_access(testapp, db_session):
    member, group, top_obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.commit()
    prior_id = top_obj.id

    # we add 4 sub items
    for i in range(4):
        t = TestObject(owner=other.persona, public=True,
                       belongs_to_id=prior_id)
        db_session.add(t)
        db_session.commit()
        prior_id = t.id

    # and another two private ones

    t = TestObject(owner=other.persona, public=False,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()
    prior_id = t.id

    t = TestObject(owner=other.persona, public=False,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()
    prior_id = t.id


    # and another public but under private.
    t = TestObject(owner=other.persona, public=True,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()


    with testapp.test_request_context() as t:
        t.user = member
        # we should find five publicly accessiable objects
        # and see none of the private from other person ones
        assert Object.query.accessible.count() == 5


def test_parent_persona_super_object_tree_access_with_shared(testapp, db_session):
    member, group, top_obj = _gen_owner(db_session)

    # someone else
    other = Login(provider="test", profile_id="other", persona=Profile())
    db_session.add(other)
    db_session.commit()
    prior_id = top_obj.id

    # we add 4 sub items
    for i in range(4):
        t = TestObject(owner=other.persona, public=True,
                       belongs_to_id=prior_id)
        db_session.add(t)
        db_session.commit()
        prior_id = t.id


    # direct of a public one, but still private
    t = TestObject(owner=other.persona, public=False,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()


    # add another private but shared with us
    t = TestObject(owner=other.persona, public=False,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()
    db.session.add(SharedWith(object_id=t.id, persona_id=member.persona.id, level="view"))
    prior_id = t.id

    # public and direct of the shared one
    t = TestObject(owner=other.persona, public=True,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()

    # direct of the shared one, but still extra private
    t = TestObject(owner=other.persona, public=False,
                   belongs_to_id=prior_id)
    db_session.add(t)
    db_session.commit()

    with testapp.test_request_context() as t:
        t.user = member
        # we should find five publicly accessiable objects
        # and see none of the private from other person ones
        assert Object.query.accessible.count() == 7
