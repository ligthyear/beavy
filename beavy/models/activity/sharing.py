from ..activity import Activity
from sqlalchemy import event, DDL
from ..object import SharedWith
from beavy.utils.db_helpers import on_table_create

class Shared(Activity):
    """
    This Activity represents an object having been shared with
    someone else
    """
    __mapper_args__ = {
        'polymorphic_identity': "shared"
    }


class Unshared(Activity):
    """
    This Activity represents a share having been removed for
    a third party
    """
    __mapper_args__ = {
        'polymorphic_identity': "unshared"
    }


on_table_create(SharedWith, DDL("""
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
""").execute_if(dialect='postgresql'))
