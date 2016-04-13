"""Adding SharedWith Model

Revision ID: 2f0af8846e21
Revises: 5e160f999311
Create Date: 2016-03-31 06:32:12.588466

"""

# revision identifiers, used by Alembic.
revision = '2f0af8846e21'
down_revision = '5e160f999311'

# add this here in order to use revision with branch_label
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('object_shared',
                    sa.Column('object_id', sa.Integer(), nullable=False),
                    sa.Column('persona_id', sa.Integer(), nullable=False),
                    sa.Column('level', sa.String(length=20), nullable=False),
                    sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ),
                    sa.ForeignKeyConstraint(['persona_id'], ['persona.id'], ),
                    sa.PrimaryKeyConstraint('object_id', 'persona_id'),
                    sa.UniqueConstraint('object_id', 'persona_id')
                    )


def downgrade():
    op.drop_table('object_shared')
