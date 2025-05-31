"""add gym_access_ids table

Revision ID: add_gym_access_ids
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_gym_access_ids'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'gym_access_ids',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=12), nullable=False),
        sa.Column('type', sa.Enum('normal', 'premium', name='gym_id_type'), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_gym_access_ids_code'), 'gym_access_ids', ['code'], unique=True)
    op.create_index(op.f('ix_gym_access_ids_id'), 'gym_access_ids', ['id'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_gym_access_ids_id'), table_name='gym_access_ids')
    op.drop_index(op.f('ix_gym_access_ids_code'), table_name='gym_access_ids')
    op.drop_table('gym_access_ids') 