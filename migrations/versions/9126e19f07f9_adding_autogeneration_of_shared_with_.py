"""Adding Autogeneration of shared with activities

Revision ID: 9126e19f07f9
Revises: 2f0af8846e21
Create Date: 2016-03-31 22:26:44.356516

"""

# revision identifiers, used by Alembic.
revision = '9126e19f07f9'
down_revision = '2f0af8846e21'

# add this here in order to use revision with branch_label
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute(sa.text("""
        CREATE OR REPLACE FUNCTION func_sharing_updated() RETURNS TRIGGER
        AS $func_sharing_updated$
            DECLARE
            BEGIN
                IF (TG_OP = 'DELETE') OR (TG_OP = 'UPDATE') THEN
                    -- insert unshared
                    INSERT INTO activities (
                        subject_id,
                        verb,
                        object_id,
                        whom_id)
                    VALUES (
                        current_setting('beavy.current_persona_id')::integer,
                        'unshared',
                        OLD.object_id,
                        OLD.persona_id
                    );
                END IF;
                IF (TG_OP = 'INSERT') OR (TG_OP = 'UPDATE') THEN
                    -- insert shared
                    INSERT INTO activities (
                        subject_id,
                        verb,
                        object_id,
                        whom_id)
                    VALUES (
                        current_setting('beavy.current_persona_id')::integer,
                        'shared',
                        NEW.object_id,
                        NEW.persona_id
                    );
                END IF;
                RETURN NULL;
            END;
        $func_sharing_updated$ LANGUAGE plpgsql;

        CREATE TRIGGER trigger_sharing_updated AFTER INSERT OR UPDATE OR DELETE
        ON object_shared
        FOR EACH ROW EXECUTE PROCEDURE func_sharing_updated();
    """))


def downgrade():
    op.execute("DROP TRIGGER trigger_sharing_updated;")
    op.execute("DROP FUNCTION IF EXISTS func_sharing_updated;")
