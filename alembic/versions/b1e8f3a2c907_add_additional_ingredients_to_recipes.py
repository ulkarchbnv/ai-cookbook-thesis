"""add additional_ingredients to generated_recipes

Revision ID: b1e8f3a2c907
Revises: a3f9c2d1e804
Create Date: 2026-04-14 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1e8f3a2c907"
down_revision: Union[str, Sequence[str], None] = "a3f9c2d1e804"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "generated_recipes",
        sa.Column("additional_ingredients", sa.Text(), nullable=False, server_default="[]"),
    )


def downgrade() -> None:
    with op.batch_alter_table("generated_recipes") as batch_op:
        batch_op.drop_column("additional_ingredients")
