from alembic import op
import sqlalchemy as sa
import uuid

# revision identifiers, used by Alembic.
revision = '662381d00554'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user',
                    sa.Column('id', sa.String(), primary_key=True, default=str(uuid.uuid4())),
                    sa.Column('username', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False, unique=True),
                    sa.Column('password', sa.String(), nullable=False))

def downgrade():
    op.drop_table('user')
