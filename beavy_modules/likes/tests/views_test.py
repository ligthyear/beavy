from beavy.tests.helpers import api_call, TestObject
from flask import url_for

def test_simple_like_flow(authed_client, db_session):
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

    assert len(api_call(c, url_for('account.account_likes'))['data']) == 1

    # alright. let's unlike it
    assert api_call(c, url_for('object.unlike_object', obj=obj.id), method="post")['liked'] == False

    # now its gone again
    assert api_call(c, url_for('object.liked_object', obj=obj.id))['liked'] == False
    assert api_call(c, url_for('account.account_likes'))['data'] == []
