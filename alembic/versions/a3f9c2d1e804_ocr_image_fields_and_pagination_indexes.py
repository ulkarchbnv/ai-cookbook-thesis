"""ocr image fields and pagination indexes

Revision ID: a3f9c2d1e804
Revises: 67fd645820b1
Create Date: 2026-04-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3f9c2d1e804"
down_revision: Union[str, Sequence[str], None] = "67fd645820b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("ocr_extractions", sa.Column("image_path", sa.String(), nullable=True))
    op.add_column("ocr_extractions", sa.Column("image_url", sa.String(), nullable=True))

    with op.batch_alter_table("generated_recipes") as batch_op:
        batch_op.create_index(
            "ix_generated_recipes_user_saved_at",
            ["user_id", "is_saved", "saved_at"],
        )
        batch_op.create_index(
            "ix_generated_recipes_user_created_at",
            ["user_id", "created_at"],
        )

    with op.batch_alter_table("ocr_extractions") as batch_op:
        batch_op.create_index(
            "ix_ocr_extractions_user_created_at",
            ["user_id", "created_at"],
        )


def downgrade() -> None:
    with op.batch_alter_table("ocr_extractions") as batch_op:
        batch_op.drop_index("ix_ocr_extractions_user_created_at")

    with op.batch_alter_table("generated_recipes") as batch_op:
        batch_op.drop_index("ix_generated_recipes_user_created_at")
        batch_op.drop_index("ix_generated_recipes_user_saved_at")

    op.drop_column("ocr_extractions", "image_url")
    op.drop_column("ocr_extractions", "image_path")
