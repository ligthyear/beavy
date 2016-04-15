from beavy.models.object import Object
from beavy.models.persona import Person
from ..models import Like


class TestObject(Object):
    __mapper_args__ = {
        'polymorphic_identity': "test"
    }


def _create_obj(db_session):
    person = Person()
    db_session.add(person)
    obj = TestObject(owner=person)
    db_session.add(obj)
    db_session.commit()
    return obj


def test_likes_simple(db_session):
    """
    Simple test to see whether likes count are properly propagated
    """
    obj = _create_obj(db_session)

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
