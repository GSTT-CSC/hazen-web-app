"""

Revision ID: 20250226a
Revises: 1544418d922f
Create Date: 2025-02-26

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250226a'
down_revision = '8ca431ff665f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('email_authenticated', sa.Boolean(), nullable=False, server_default=sa.text('false')))




def downgrade():
    # Remove 'email_authenticated' column from 'user' table
    op.drop_column('user', 'email_authenticated')

