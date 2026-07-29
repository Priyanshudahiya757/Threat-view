"""add_auth_fields_to_users

Adds password_hash, role, and is_active to the users table.
Removes the legacy subscription column.

Revision ID: b3c4d5e6f7a8
Revises: a1b2c3d4e5f6
Create Date: 2026-07-27
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3c4d5e6f7a8'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('role', sa.String(50), nullable=True, server_default='analyst'))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default=sa.true()))

    # Back-fill so NOT NULL can be applied
    op.execute("UPDATE users SET password_hash = '' WHERE password_hash IS NULL")
    op.execute("UPDATE users SET role = 'analyst' WHERE role IS NULL")
    op.execute("UPDATE users SET is_active = true WHERE is_active IS NULL")

    with op.batch_alter_table('users') as batch_op:
        batch_op.alter_column('password_hash', nullable=False)
        batch_op.alter_column('role', nullable=False)
        batch_op.alter_column('is_active', nullable=False)
        try:
            batch_op.drop_column('subscription')
        except Exception:
            pass

    op.create_index('ix_users_role', 'users', ['role'])


def downgrade():
    op.drop_index('ix_users_role', table_name='users')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'role')
    op.drop_column('users', 'password_hash')
    op.add_column('users', sa.Column('subscription', sa.String(50), nullable=True, server_default='free'))
