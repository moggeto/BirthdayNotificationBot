"""multiple notifications

Revision ID: 8591e78b79a8
Revises: 6ee23a2cc81a
Create Date: 2026-04-13 17:19:35.738472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8591e78b79a8'
down_revision: Union[str, None] = '6ee23a2cc81a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- notification_settings ---
    op.create_table(
        "notification_settings_new",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("days_before", sa.Integer(), nullable=False),
    )

    op.execute("""
        INSERT INTO notification_settings_new (id, user_id, days_before)
        SELECT id, user_id, notify_before FROM notification_settings
    """)

    op.drop_table("notification_settings")
    op.rename_table("notification_settings_new", "notification_settings")

    op.create_index(
        "ix_notification_settings_user_id",
        "notification_settings",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "uq_user_notification_day",
        "notification_settings",
        ["user_id", "days_before"],
        unique=True,
    )

    # --- sent_notifications ---
    op.add_column(
        "sent_notifications",
        sa.Column("days_before", sa.Integer(), nullable=False, server_default="1"),
    )

    op.create_index(
        "ix_sent_notifications_user_id",
        "sent_notifications",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_sent_notifications_birthday_id",
        "sent_notifications",
        ["birthday_id"],
        unique=False,
    )

    op.create_index(
        "uq_sent_notification_once_per_day",
        "sent_notifications",
        ["user_id", "birthday_id", "date_sent", "days_before"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_sent_notification_once_per_day", table_name="sent_notifications")
    op.drop_index("ix_sent_notifications_birthday_id", table_name="sent_notifications")
    op.drop_index("ix_sent_notifications_user_id", table_name="sent_notifications")
    op.drop_column("sent_notifications", "days_before")

    op.create_table(
        "notification_settings_old",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("notify_before", sa.Integer(), nullable=False),
    )

    op.execute("""
        INSERT INTO notification_settings_old (id, user_id, notify_before)
        SELECT id, user_id, days_before FROM notification_settings
    """)

    op.drop_index("uq_user_notification_day", table_name="notification_settings")
    op.drop_index("ix_notification_settings_user_id", table_name="notification_settings")
    op.drop_table("notification_settings")
    op.rename_table("notification_settings_old", "notification_settings")

    op.create_index(
        "ix_notification_settings_user_id",
        "notification_settings",
        ["user_id"],
        unique=True,
    )