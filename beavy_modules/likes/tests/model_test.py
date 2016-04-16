from beavy.models.persona import Person
from beavy.models.login import Login
from ..models import Like
from beavy.tests.helpers import TestObject


def test_likes_simple(db_session):
    """
    Simple test to see whether likes count are properly propagated
    """

    login = Login(persona=Person(), provider="test", profile_id="test")
    db_session.add(login)
    obj = TestObject(owner=login.persona)
    db_session.add(obj)
    db_session.commit()

    assert obj.likes_count == 0
    assert not obj.likes_updated

    db_session.add(Like(object=obj, subject=obj.owner))
    db_session.commit()

    db_session.expire(obj)
    db_session.refresh(obj)

    assert obj.likes_count == 1
    assert not not obj.likes_updated

    db_session.delete(Like.query.first())
    db_session.commit()

    db_session.expire(obj)
    db_session.refresh(obj)

    assert obj.likes_count == 0
    assert not not obj.likes_updated
