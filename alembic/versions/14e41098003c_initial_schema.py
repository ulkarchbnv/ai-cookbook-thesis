"""initial schema

Revision ID: 14e41098003c
Revises:
Create Date: 2026-04-12 21:00:06.728526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "14e41098003c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the original persisted schema from scratch.

    This baseline intentionally includes the legacy ``recipes`` table because the
    next revision removes it. New databases can now follow the full migration
    chain instead of depending on pre-existing tables/indexes.
    """
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("preferences", sa.Text(), server_default="[]", nullable=False),
        sa.Column("allergies", sa.Text(), server_default="[]", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "generated_recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fingerprint", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=False),
        sa.Column("preferences", sa.Text(), server_default="[]", nullable=False),
        sa.Column("allergies", sa.Text(), server_default="[]", nullable=False),
        sa.Column("steps", sa.Text(), nullable=False),
        sa.Column("nutrition", sa.Text(), nullable=False),
        sa.Column("warnings", sa.Text(), server_default="[]", nullable=False),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("image_cache_key", sa.String(), nullable=True),
        sa.Column("image_prompt", sa.Text(), nullable=True),
        sa.Column("is_saved", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("saved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_generated_recipes_fingerprint"), "generated_recipes", ["fingerprint"], unique=False)
    op.create_index(op.f("ix_generated_recipes_id"), "generated_recipes", ["id"], unique=False)
    op.create_index(op.f("ix_generated_recipes_image_cache_key"), "generated_recipes", ["image_cache_key"], unique=False)

    op.create_table(
        "recipes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=False),
        sa.Column("steps", sa.Text(), nullable=False),
        sa.Column("nutrition", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("preferences", sa.Text(), server_default="[]", nullable=False),
        sa.Column("allergies", sa.Text(), server_default="[]", nullable=False),
        sa.Column("image_cache_key", sa.String(), nullable=True),
        sa.Column("image_path", sa.String(), nullable=True),
        sa.Column("image_prompt", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recipes_id"), "recipes", ["id"], unique=False)
    op.create_index(op.f("ix_recipes_image_cache_key"), "recipes", ["image_cache_key"], unique=False)

    op.create_table(
        "ocr_extractions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source_filename", sa.String(), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_nutrition", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ocr_extractions_id"), "ocr_extractions", ["id"], unique=False)


def downgrade() -> None:
    """Drop the original persisted schema."""
    op.drop_index(op.f("ix_ocr_extractions_id"), table_name="ocr_extractions")
    op.drop_table("ocr_extractions")

    op.drop_index(op.f("ix_recipes_image_cache_key"), table_name="recipes")
    op.drop_index(op.f("ix_recipes_id"), table_name="recipes")
    op.drop_table("recipes")

    op.drop_index(op.f("ix_generated_recipes_image_cache_key"), table_name="generated_recipes")
    op.drop_index(op.f("ix_generated_recipes_id"), table_name="generated_recipes")
    op.drop_index(op.f("ix_generated_recipes_fingerprint"), table_name="generated_recipes")
    op.drop_table("generated_recipes")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
