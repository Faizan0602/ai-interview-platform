"""create_answers_table

Revision ID: d14c2a92f0a1
Revises: be05a9d20ad0
Create Date: 2026-09-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d14c2a92f0a1"
down_revision: Union[str, Sequence[str], None] = "be05a9d20ad0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    if "feedback" in tables:
        op.drop_table("feedback")

    if "answers" in tables:
        _upgrade_existing_answers_table(inspector)
    else:
        _create_answers_table()

    inspector = sa.inspect(bind)
    if "interview_sessions" in inspector.get_table_names():
        op.drop_table("interview_sessions")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_answers_user_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_question_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_id"), table_name="answers")
    op.drop_table("answers")


def _create_answers_table() -> None:
    op.create_table(
        "answers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("question_id", sa.UUID(), nullable=False),
        sa.Column("answer_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_answers_id"), "answers", ["id"], unique=False)
    op.create_index(op.f("ix_answers_question_id"), "answers", ["question_id"], unique=False)
    op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)


def _upgrade_existing_answers_table(inspector: sa.Inspector) -> None:
    columns = {column["name"] for column in inspector.get_columns("answers")}

    if "user_id" in columns:
        _ensure_answers_user_id_index(inspector)
        return

    if "session_id" not in columns:
        op.drop_table("answers")
        _create_answers_table()
        return

    op.add_column("answers", sa.Column("user_id", sa.UUID(), nullable=True))
    op.execute(
        sa.text(
            """
            UPDATE answers
            SET user_id = interview_sessions.user_id
            FROM interview_sessions
            WHERE answers.session_id = interview_sessions.id
            """
        )
    )
    op.execute(sa.text("DELETE FROM answers WHERE user_id IS NULL"))

    indexes = {index["name"] for index in inspector.get_indexes("answers")}
    if op.f("ix_answers_session_id") in indexes:
        op.drop_index(op.f("ix_answers_session_id"), table_name="answers")

    unique_constraints = {
        constraint["name"]
        for constraint in inspector.get_unique_constraints("answers")
    }
    if "uq_session_question_answer" in unique_constraints:
        op.drop_constraint("uq_session_question_answer", "answers", type_="unique")

    for foreign_key in inspector.get_foreign_keys("answers"):
        if foreign_key["constrained_columns"] == ["session_id"]:
            op.drop_constraint(foreign_key["name"], "answers", type_="foreignkey")

    op.drop_column("answers", "session_id")
    op.alter_column("answers", "user_id", existing_type=sa.UUID(), nullable=False)
    op.create_foreign_key(
        None,
        "answers",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)


def _ensure_answers_user_id_index(inspector: sa.Inspector) -> None:
    indexes = {index["name"] for index in inspector.get_indexes("answers")}
    if op.f("ix_answers_user_id") not in indexes:
        op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)
