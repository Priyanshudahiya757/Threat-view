"""Add malware_family, reputation columns and alert/brand tables."""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "4f08de9202b6"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("threats", schema=None) as batch_op:
        batch_op.add_column(sa.Column("malware_family", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("reputation", sa.String(length=20), server_default="unknown", nullable=False))
        batch_op.create_index(batch_op.f("ix_threats_malware_family"), ["malware_family"], unique=False)
        batch_op.create_index(batch_op.f("ix_threats_reputation"), ["reputation"], unique=False)

    op.create_table(
        "alert_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("rule_type", sa.String(length=50), nullable=False),
        sa.Column("rule_value", sa.String(length=512), nullable=False),
        sa.Column("notify_dashboard", sa.Boolean(), nullable=False),
        sa.Column("notify_email", sa.Boolean(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("alert_rules", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_alert_rules_is_active"), ["is_active"], unique=False)
        batch_op.create_index(batch_op.f("ix_alert_rules_rule_type"), ["rule_type"], unique=False)

    op.create_table(
        "alert_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rule_id", sa.Integer(), nullable=True),
        sa.Column("threat_id", sa.Integer(), nullable=True),
        sa.Column("alert_type", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=False),
        sa.Column("email_sent", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["rule_id"], ["alert_rules.id"]),
        sa.ForeignKeyConstraint(["threat_id"], ["threats.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("alert_events", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_alert_events_alert_type"), ["alert_type"], unique=False)
        batch_op.create_index(batch_op.f("ix_alert_events_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_alert_events_is_read"), ["is_read"], unique=False)
        batch_op.create_index(batch_op.f("ix_alert_events_rule_id"), ["rule_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_alert_events_threat_id"), ["threat_id"], unique=False)

    op.create_table(
        "brand_monitors",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_domain", sa.String(length=255), nullable=False),
        sa.Column("notify_dashboard", sa.Boolean(), nullable=False),
        sa.Column("notify_email", sa.Boolean(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("brand_monitors", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_brand_monitors_company_domain"), ["company_domain"], unique=True)
        batch_op.create_index(batch_op.f("ix_brand_monitors_is_active"), ["is_active"], unique=False)


def downgrade():
    with op.batch_alter_table("brand_monitors", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_brand_monitors_is_active"))
        batch_op.drop_index(batch_op.f("ix_brand_monitors_company_domain"))
    op.drop_table("brand_monitors")

    with op.batch_alter_table("alert_events", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_alert_events_threat_id"))
        batch_op.drop_index(batch_op.f("ix_alert_events_rule_id"))
        batch_op.drop_index(batch_op.f("ix_alert_events_is_read"))
        batch_op.drop_index(batch_op.f("ix_alert_events_created_at"))
        batch_op.drop_index(batch_op.f("ix_alert_events_alert_type"))
    op.drop_table("alert_events")

    with op.batch_alter_table("alert_rules", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_alert_rules_rule_type"))
        batch_op.drop_index(batch_op.f("ix_alert_rules_is_active"))
    op.drop_table("alert_rules")

    with op.batch_alter_table("threats", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_threats_reputation"))
        batch_op.drop_index(batch_op.f("ix_threats_malware_family"))
        batch_op.drop_column("reputation")
        batch_op.drop_column("malware_family")
