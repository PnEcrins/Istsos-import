"""add time zone

Revision ID: 48686f780067
Revises: ec081d1930de
Create Date: 2022-10-26 12:07:27.529161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "48686f780067"
down_revision = "ec081d1930de"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        ALTER TABLE public.imports
        ADD column timezone character varying(255)
        """
    )


def downgrade():
    op.execute(
        """
        ALTER TABLE public.imports
        DROP column timezone;
        """
    )
