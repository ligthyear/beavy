"""Initial Persona and Objects infrastructure

Revision ID: ba94d00549a9
Revises: None
Create Date: 2016-03-27 19:55:17.958111

"""

# revision identifiers, used by Alembic.
revision = 'ba94d00549a9'
down_revision = None

# add this here in order to use revision with branch_label
branch_labels = ('beavy', )

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


def upgrade():
    op.create_table('persona',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=25), nullable=True),
                    sa.Column('pretty_name', sa.String(length=100),
                              nullable=True),
                    sa.Column('type', sa.String(length=100), nullable=False),
                    sa.Column('created_at', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('active', sa.Boolean(), nullable=True),
                    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
                    sa.Column('last_login_at', sa.DateTime(), nullable=True),
                    sa.Column('current_login_at', sa.DateTime(),
                              nullable=True),
                    sa.Column('last_login_ip', sa.String(length=255),
                              nullable=True),
                    sa.Column('current_login_ip', sa.String(length=255),
                              nullable=True),
                    sa.Column('login_count', sa.Integer(), nullable=True),
                    sa.Column('language_preference', sa.String(length=2),
                              nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('name')
                    )

    op.create_table('login',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('persona_id', sa.Integer(), nullable=False),
                    sa.Column('provider', sa.String(length=255),
                              nullable=False),
                    sa.Column('profile_id', sa.String(length=255),
                              nullable=False),
                    sa.Column('username', sa.String(length=255),
                              nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('access_token', sa.String(length=255),
                              nullable=True),
                    sa.Column('secret', sa.String(length=255), nullable=True),
                    sa.Column('first_name', sa.String(length=255),
                              nullable=True),
                    sa.Column('last_name', sa.String(length=255),
                              nullable=True),
                    sa.Column('cn', sa.String(length=255), nullable=True),
                    sa.Column('profile_url', sa.String(length=512),
                              nullable=True),
                    sa.Column('image_url', sa.String(length=512),
                              nullable=True),
                    sa.ForeignKeyConstraint(['persona_id'], ['persona.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('objects',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('type', sa.String(length=100), nullable=False),
                    sa.Column('created_at', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('payload', postgresql.JSONB(), nullable=True),
                    sa.Column('owner_id', sa.Integer(), nullable=False),
                    sa.Column('belongs_to_id', sa.Integer(), nullable=True),
                    sa.Column('public', sa.Boolean(), nullable=False),
                    sa.Column('in_reply_to_id', sa.Integer(), nullable=True),
                    sa.Column('likes_count', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['belongs_to_id'],
                                            ['objects.id'], ),
                    sa.ForeignKeyConstraint(['in_reply_to_id'],
                                            ['objects.id'], ),
                    sa.ForeignKeyConstraint(['owner_id'],
                                            ['persona.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('persona_roles',
                    sa.Column('source_id', sa.Integer(), nullable=False),
                    sa.Column('target_id', sa.Integer(), nullable=False),
                    sa.Column('role', sa.String(length=20), nullable=False),
                    sa.ForeignKeyConstraint(['source_id'], ['persona.id'], ),
                    sa.ForeignKeyConstraint(['target_id'], ['persona.id'], ),
                    sa.PrimaryKeyConstraint('source_id', 'target_id'),
                    sa.UniqueConstraint('source_id', 'target_id')
                    )

    op.create_table('activities',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('subject_id', sa.Integer(), nullable=False),
                    sa.Column('verb', sa.String(length=100), nullable=False),
                    sa.Column('created_at', sa.DateTime(),
                              server_default=sa.text('now()'), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('whom_id', sa.Integer(), nullable=True),
                    sa.Column('payload', postgresql.JSONB(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['objects.id'], ),
                    sa.ForeignKeyConstraint(['subject_id'], ['persona.id'], ),
                    sa.ForeignKeyConstraint(['whom_id'], ['persona.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('activities')
    op.drop_table('persona_roles')
    op.drop_table('objects')
    op.drop_table('login')
    op.drop_table('persona')
