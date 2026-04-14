""" display_hebrew_date

Revision ID: 9a130df84526
Revises: 67310b201e3a
Create Date: 2026-04-14 17:16:04.724334

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a130df84526'
down_revision: Union[str, None] = '67310b201e3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



notification_calendar_mode_enum = sa.Enum(
    "gregorian",
    "hebrew",
    "both",
    name="notificationcalendarmode",
)


def upgrade() -> None:
    with op.batch_alter_table("birthdays", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "notification_calendar_mode",
                notification_calendar_mode_enum,
                nullable=False,
                server_default="gregorian",
            )
        )

    with op.batch_alter_table("birthday_dates", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_derived",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("birthday_dates", schema=None) as batch_op:
        batch_op.drop_column("is_derived")

    with op.batch_alter_table("birthdays", schema=None) as batch_op:
        batch_op.drop_column("notification_calendar_mode")