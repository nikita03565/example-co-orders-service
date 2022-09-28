# pylint: skip-file
"""Fixes migrations conflict.
Generated with "alembic merge heads"

Revision ID: 6b47565d3ece
Revises: d3bdae443a1a, 52ad861d3c4c
Create Date: 2022-09-20 13:24:15.073156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6b47565d3ece"
down_revision = ("d3bdae443a1a", "52ad861d3c4c")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
