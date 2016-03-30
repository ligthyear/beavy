from beavy.app import app, db
from beavy.models.persona import Persona, Role
from beavy.models.profile import Profile
from beavy.models.organisation import Organisation
from beavy.models.login import Login


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
