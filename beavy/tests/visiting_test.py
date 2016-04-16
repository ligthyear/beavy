from beavy.models.object import External
from beavy.tests.helpers import api_call, TestObject
from beavy.models.persona import Person
from flask import url_for


def test_simple_visit_flow(authed_client, db_session):
    c = authed_client

    obj = TestObject(owner=c.login.persona)
    db_session.add(obj)
    db_session.commit()

    assert api_call(c, url_for('object.visited', object=obj.id))['visited'] == False

    assert api_call(c, url_for('object.visit', object=obj.id))['visited'] == True

    assert api_call(c, url_for('object.visited', object=obj.id))['visited'] == True


def test_simple_visit_external_flow(authed_client, db_session):
    c = authed_client

    obj = External(owner=c.login.persona, payload={'link':'http://www.google.com/test?q=1'})
    db_session.add(obj)
    db_session.commit()

    assert api_call(c, url_for('object.visited', object=obj.id))['visited'] == False

    # going there 'externally'
    resp = c.get(url_for('object.external', object=obj.id))
    assert resp.status_code == 302
    assert resp.headers['Location'] == 'http://www.google.com/test?q=1'

    assert api_call(c, url_for('object.visited', object=obj.id))['visited'] == True
