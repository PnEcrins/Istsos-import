"""add role and admin

Revision ID: 827976481314
Revises: a6c2d82e9f67
Create Date: 2023-02-14 14:41:14.248099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "827976481314"
down_revision = "a6c2d82e9f67"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
    	INSERT INTO roles(name) VALUES ('ADMIN'), ('USER');
    	"""
    )
    op.execute(
        """
        INSERT INTO users(user_uuid, firstname, surname, login, pwd, email, id_role)
        VALUES (uuid_generate_v4(), 'admin', 'admin', 'admin', 'pbkdf2:sha256:260000$6lp00MzgXlhhsaSH$e4255098c22b36492f7942be37b6ca55accf03f49acd6d7b7226b428f413926e', 'test@tobechange.com', (SELECT id FROM roles where name = 'ADMIN'))
        """
    )


def downgrade():
    pass
