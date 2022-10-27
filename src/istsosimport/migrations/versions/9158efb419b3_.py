"""empty message

Revision ID: 9158efb419b3
Revises: 48686f780067
Create Date: 2022-10-27 12:10:33.075364

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9158efb419b3'
down_revision = '48686f780067'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('mapping',
    sa.Column('id_mapping', sa.Integer(), nullable=False),
    sa.Column('name', sa.Unicode(), nullable=True),
    sa.Column('id_opr', sa.Integer(), nullable=True),
    sa.Column('column_name', sa.Unicode(), nullable=True),
    sa.PrimaryKeyConstraint('id_mapping'),
    schema='public'
    )


def downgrade():
    op.drop_table('mapping', schema='public')
