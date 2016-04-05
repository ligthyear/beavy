"""Add Personal Messaging Framework

Revision ID: 5e160f999311
Revises: ba94d00549a9
Create Date: 2016-03-27 20:04:03.751098

"""

# revision identifiers, used by Alembic.
revision = '5e160f999311'
down_revision = 'ba94d00549a9'

# add this here in order to use revision with branch_label
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('private_message_participants',
                    sa.Column('persona_id', sa.Integer(), nullable=False),
                    sa.Column('pm_id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['persona_id'], ['persona.id'], ),
                    sa.ForeignKeyConstraint(['pm_id'], ['objects.id'], )
                    )


def downgrade():
    op.drop_table('private_message_participants')
