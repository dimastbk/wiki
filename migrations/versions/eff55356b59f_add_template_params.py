"""add template_params

Revision ID: eff55356b59f
Revises: 03667a1c8139
Create Date: 2022-02-11 11:41:07.028114

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "eff55356b59f"
down_revision = "03667a1c8139"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "namespace",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("number", sa.SmallInteger(), nullable=True),
        sa.Column("name", sa.String(length=191), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "project",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=191), nullable=True),
        sa.Column("update_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "template",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=191), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_template_title"), "template", ["title"], unique=False)
    op.create_table(
        "page",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=191), nullable=True),
        sa.Column("wiki_id", sa.BigInteger(), nullable=True),
        sa.Column("namespace_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_page_namespace_id"), "page", ["namespace_id"], unique=False
    )
    op.create_index(op.f("ix_page_title"), "page", ["title"], unique=False)
    op.create_table(
        "page_template",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("template_id", sa.BigInteger(), nullable=True),
        sa.Column("page_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["page_id"],
            ["page.id"],
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["template.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_page_template_page_id"), "page_template", ["page_id"], unique=False
    )
    op.create_index(
        op.f("ix_page_template_template_id"),
        "page_template",
        ["template_id"],
        unique=False,
    )
    op.create_table(
        "param",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("page_template_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=191), nullable=True),
        sa.Column("value", sa.String(length=1000), nullable=True),
        sa.ForeignKeyConstraint(
            ["page_template_id"],
            ["page_template.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_param_name"), "param", ["name"], unique=False)
    op.create_index(
        op.f("ix_param_page_template_id"), "param", ["page_template_id"], unique=False
    )
    op.create_index(
        op.f("ix_gkgn_object_type_id"), "gkgn_object", ["type_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_gkgn_object_type_id"), table_name="gkgn_object")
    op.drop_index(op.f("ix_param_page_template_id"), table_name="param")
    op.drop_index(op.f("ix_param_name"), table_name="param")
    op.drop_table("param")
    op.drop_index(op.f("ix_page_template_template_id"), table_name="page_template")
    op.drop_index(op.f("ix_page_template_page_id"), table_name="page_template")
    op.drop_table("page_template")
    op.drop_index(op.f("ix_page_title"), table_name="page")
    op.drop_index(op.f("ix_page_namespace_id"), table_name="page")
    op.drop_table("page")
    op.drop_index(op.f("ix_template_title"), table_name="template")
    op.drop_table("template")
    op.drop_table("project")
    op.drop_table("namespace")
    # ### end Alembic commands ###
