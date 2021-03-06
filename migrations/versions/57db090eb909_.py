"""

Revision ID: 57db090eb909
Revises: 
Create Date: 2020-09-08 23:18:18.400076

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57db090eb909'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('index', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.Unicode(), nullable=True),
    sa.Column('last_name', sa.Unicode(), nullable=True),
    sa.Column('username', sa.Unicode(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), server_default=sa.text('false'), nullable=True),
    sa.Column('start_conversation', sa.Boolean(), server_default=sa.text('false'), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('index')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
