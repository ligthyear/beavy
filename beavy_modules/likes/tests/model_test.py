from beavy.models.object import Object
from beavy.models.persona import Person
from beavy.models.login import Login
from contextlib import contextmanager
from flask import appcontext_pushed, g
from ..models import Like

from flask import url_for

import pytest
import json

class TestObject(Object):
    __mapper_args__ = {
        'polymorphic_identity': "test"
    }


def _create_obj(db_session):
    login = Login(persona=Person(), provider="test", profile_id="test")
    db_session.add(login)
    obj = TestObject(owner=login.persona)
    db_session.add(obj)
    db_session.commit()
    return (obj, login)


def _get_json(client, query, expected_code=200, method="get"):
    mth = getattr(client, method)
    resp = mth(query, headers=[('Accept', 'application/vnd.api+json')])
    if expected_code:
        assert resp.status_code == expected_code, "Wrong Status Code"
    return json.loads(resp.get_data(as_text=True))


@pytest.yield_fixture(scope='function')
def logged_in_session(testapp, db_session):
    obj, login = _create_obj(db_session)
    with testapp.test_client() as c:
        with c.session_transaction() as sess:
            sess['user_id'] = login.id
            sess['_fresh'] = True
        yield (c, login, obj)


def test_likes_simple(db_session):
    """
    Simple test to see whether likes count are properly propagated
    """
    obj, _ = _create_obj(db_session)

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

def test_simple_like_flow(logged_in_session):
    c, login, obj = logged_in_session

    # nothing yet:
    assert _get_json(c, url_for('account.account_likes'))['data'] == []

    assert _get_json(c, url_for('object.liked_object', obj=obj.id))['liked'] == False

    # alright. let's like it
    assert _get_json(c, url_for('object.like_object', obj=obj.id), method="post")['liked'] == True

    # now it shows up
    assert _get_json(c, url_for('object.liked_object', obj=obj.id))['liked'] == True

    assert len(_get_json(c, url_for('account.account_likes'))['data']) == 1

    # alright. let's unlike it
    assert _get_json(c, url_for('object.unlike_object', obj=obj.id), method="post")['liked'] == False

    # now its gone again
    assert _get_json(c, url_for('object.liked_object', obj=obj.id))['liked'] == False
    assert _get_json(c, url_for('account.account_likes'))['data'] == []
