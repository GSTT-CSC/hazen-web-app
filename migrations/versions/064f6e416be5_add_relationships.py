"""add relationships

Revision ID: 064f6e416be5
Revises: 5b29621c4aea
Create Date: 2024-03-07 23:00:56.518640

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "064f6e416be5"
down_revision = "5b29621c4aea"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("series", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", postgresql.UUID(), nullable=True))
        batch_op.add_column(sa.Column("device_id", postgresql.UUID(), nullable=True))
        batch_op.add_column(sa.Column("study_id", postgresql.UUID(), nullable=True))
        batch_op.create_foreign_key(None, "user", ["user_id"], ["id"])
        batch_op.create_foreign_key(None, "study", ["study_id"], ["id"])
        batch_op.create_foreign_key(None, "device", ["device_id"], ["id"])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("series", schema=None) as batch_op:
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_constraint(None, type_="foreignkey")
        batch_op.drop_column("study_id")
        batch_op.drop_column("device_id")
        batch_op.drop_column("user_id")

    # ### end Alembic commands ###
