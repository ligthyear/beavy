from beavy.app import app, db
from beavy.models.persona import Persona, Role, Profile, Organisation
from werkzeug.exceptions import BadRequest
from beavy.models.login import Login

import pytest

CURRENT_PERSONA_QUERY = "SHOW beavy.current_persona_id"


def _gen_member(db_session):
    group = Organisation(name="test_group")

    # no membership
    groupie = Login(provider="test", profile_id="normal", persona=Profile())
    db_session.add(group)
    db_session.add(groupie)

    db_session.commit()

    db_session.add(Role(source_id=groupie.persona_id,
                        target_id=group.id,
                        role="member"))
    db_session.commit()
    return (groupie, group)


def test_default_current_persona(testapp, db_session):
    """
    Default persona of a login is the persona itself
    """
    with testapp.test_request_context():
        l = Login(provider="test", profile_id="test", persona=Profile())
        db_session.add(l)
        db_session.commit()
        assert l.current_persona == l.persona


def test_ensure_system_persona(testapp, db_session):
    """
    If we have an app and access its system_persona, IT MUST BE SET
    """
    with testapp.test_request_context():
        testapp.system_persona.id == testapp.system_persona_id


def test_login_roles(testapp, db_session):
    """
    If we have an app and access its system_persona, IT MUST BE SET
    """
    with testapp.test_request_context():
        system_persona = testapp.system_persona
        other_group = Organisation()

        # no membership
        normal = Login(provider="test", profile_id="normal", persona=Profile())
        # other membership
        groupie = Login(provider="test", profile_id="groupie",
                        persona=Profile())
        # admin of the system
        admin = Login(provider="test", profile_id="admin", persona=Profile())
        # moderator of the system
        mod = Login(provider="test", profile_id="admin", persona=Profile())

        db_session.add(other_group)
        db_session.add(normal)
        db_session.add(groupie)
        db_session.add(admin)
        db_session.add(mod)
        db_session.commit()

        db_session.add(Role(source_id=groupie.persona_id,
                            target_id=other_group.id,
                            role="admin"))

        db_session.add(Role(source_id=admin.persona_id,
                            target_id=system_persona.id,
                            role="admin"))

        db_session.add(Role(source_id=mod.persona_id,
                            target_id=system_persona.id,
                            role="moderator"))


        db_session.commit()

        assert normal.roles == []
        assert groupie.roles == []
        assert len(admin.roles) == 1 and admin.roles[0].name == "admin"
        assert len(mod.roles) == 1  and mod.roles[0].name == "moderator"

        assert normal.is_staff is False
        assert groupie.is_staff is False
        assert admin.is_staff is True
        assert mod.is_staff is True



def test_current_persona_id(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context():
        member.current_persona == member.persona
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == member.persona.id


def test_current_group_persona_id(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": group.id}):
        member.current_persona == group
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == group.id


def test_current_group_persona_id_string(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": "{}".format(group.id)}):
        member.current_persona == group
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == group.id


def test_current_group_persona_name(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": group.name}):
        member.current_persona == group
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == group.id

    with testapp.test_request_context():
        member.current_persona == persona
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == persona.id


def test_session_persona_reset_between_connections(testapp, db_session):
    """
    This test ensure that the connection is cleaned up properly before
    being reused and we aren't leaking the previously set current_persona_id
    setting
    """
    # we have exactly one connection in our pool at any time!
    assert db.engine.pool.size() == 1

    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": group.name}):
        member.current_persona == group
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == group.id

    db_session.close() # close on the current session

    # as we have only one connection in the pool, we receive the same
    # connection and can make sure that is not having any persona set
    other_session = db.create_scoped_session()
    assert other_session.execute(CURRENT_PERSONA_QUERY).scalar() == ''


def test_current_group_persona_name(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": group.name}):
        member.current_persona == group
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == group.id


@pytest.mark.xfail(raises=BadRequest)
def test_current_group_persona_fails(testapp, db_session):
    member, group = _gen_member(db_session)
    with testapp.test_request_context(headers={"X-Act-As-Identity": 123}):
        member.current_persona == False


def test_higher_persona_test_id(testapp, db_session):
    holding = Organisation(name="Higher Holding")
    db_session.add(holding)

    member, group = _gen_member(db_session)

    db_session.add(Role(source_id=group.id,
                        target_id=holding.id,
                        role="member"))
    db_session.commit()
    with testapp.test_request_context(headers={"X-Act-As-Identity": holding.id}):
        member.current_persona == holding
        assert int(db_session.scalar(CURRENT_PERSONA_QUERY)) == holding.id
