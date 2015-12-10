"""Removing Link, making everything a topic object

Revision ID: 5a62a907d38
Revises: 1d461753b2e
Create Date: 2015-12-07 04:20:40.833528

"""

# revision identifiers, used by Alembic.
revision = '5a62a907d38'
depends_on = '1d461753b2e'
down_revision = None

# add this here in order to use revision with branch_label
branch_labels = ('beavy.hive',)

from alembic import op
from sqlalchemy.orm import sessionmaker

from beavy_modules.url_extractor.tasks import extract_for_model


def upgrade():

    connection = op.get_bind()
    SessionMaker = sessionmaker(bind=connection.engine)
    session = SessionMaker(bind=connection)

    ids_to_update = [row[0] for row in
                     session.query("""ID FROM objects
                                   WHERE type='link'""")]

    session.execute("""UPDATE objects
                        SET type='topic'
                    WHERE type='link' """)

    for id in ids_to_update:
        extract_for_model.delay(id)


def downgrade():
    pass
