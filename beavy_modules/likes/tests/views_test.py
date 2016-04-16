from beavy.tests.helpers import api_call, TestObject
from beavy.models.persona import Person
from flask import url_for


def test_simple_like_flow(authed_client, ListedTestObject, db_session):
    c = authed_client

    obj = ListedTestObject(owner=c.login.persona)
    db_session.add(obj)
    db_session.commit()

    # nothing yet:
    assert api_call(c, url_for('account.account_likes'))['data'] == []

    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == False

    # alright. let's like it
    assert api_call(c, url_for('object.like_object', obj=obj.id), method="post")['liked'] == True

    # now it shows up
    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == True

    assert len(api_call(c, url_for('account.account_likes'))['data']) == 1

    # alright. let's unlike it
    assert api_call(c, url_for('object.unlike_object', obj=obj.id), method="post")['liked'] == False

    # now its gone again
    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == False
    assert api_call(c, url_for('account.account_likes'))['data'] == []



def test_unlisted_stay_unlisted(authed_client, db_session):
    """
    We are liking and unliking an "unlisted" Object, should
    all work aside from it showing up in the list
    """
    c = authed_client

    obj = TestObject(owner=c.login.persona)
    db_session.add(obj)
    db_session.commit()

    # nothing yet:
    assert api_call(c, url_for('account.account_likes'))['data'] == []

    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == False

    # alright. let's like it
    assert api_call(c, url_for('object.like_object', obj=obj.id), method="post")['liked'] == True

    # now it shows up
    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == True

    assert len(api_call(c, url_for('account.account_likes'))['data']) == 0

    # alright. let's unlike it
    assert api_call(c, url_for('object.unlike_object', obj=obj.id), method="post")['liked'] == False

    # now its gone again
    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == False
    assert api_call(c, url_for('account.account_likes'))['data'] == []


def test_unaccessible(authed_client, db_session):
    """
    We are liking and unliking an Object we can't access, should fail
    apropriately.
    """
    c = authed_client

    other = Person()
    db_session.add(other)

    obj = TestObject(owner=other, public=False)
    db_session.add(obj)
    db_session.commit()

    # nothing yet:
    assert api_call(c, url_for('account.account_likes'))['data'] == []

    # comes back with a 403
    api_call(c, url_for('object.liked_object', obj=obj.id),
             expected_code=403)

    # comes back with a 403
    api_call(c, url_for('object.like_object', obj=obj.id),
            method="post", expected_code=403)

    # and nothing changed
    assert len(api_call(c, url_for('account.account_likes'))['data']) == 0

    # alright. unlike doesn't work either
    assert api_call(c, url_for('object.unlike_object', obj=obj.id),
            method="post", expected_code=403)
