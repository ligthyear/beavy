"""empty message

Revision ID: 27cb2ef1510
Revises: 1d461753b2e
Create Date: 2016-02-28 21:10:07.051303

"""

# revision identifiers, used by Alembic.
revision = '27cb2ef1510'
down_revision = '1d461753b2e'

# add this here in order to use revision with branch_label
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('language_preference', sa.String(length=2), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'language_preference')
    ### end Alembic commands ###
