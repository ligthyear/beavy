from beavy.app import db
from sqlalchemy import text


BEAVY_PERSONA_SETTING_KEY = "beavy.current_persona_id"


def set_db_persona(persona):
    if hasattr(persona, "id"):
        persona = persona.id

    db.session.execute(text("""
        SET session "{}" = :persona_id
    """.format(BEAVY_PERSONA_SETTING_KEY)), {"persona_id": persona})
