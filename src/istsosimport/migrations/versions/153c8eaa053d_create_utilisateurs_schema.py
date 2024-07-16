"""create utilisateurs schema

Revision ID: 153c8eaa053d
Revises: 827976481314
Create Date: 2024-07-12 17:25:14.735842

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '153c8eaa053d'
down_revision = '827976481314'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE SCHEMA utilisateurs")


def downgrade():
    op.execute("DROP SCHEMA utilisateurs")
