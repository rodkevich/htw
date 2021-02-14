import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from frontend.migrations import metadata
from frontend.users.enums import UserGender

__all__ = [
    "users",
    "permissions",
    "gender_enum",
]

gender_enum = postgresql.ENUM(UserGender)

# users = sa.Table(
#     "users",
#     metadata,
#     sa.Column("id", sa.Integer, primary_key=True, index=True),
#     sa.Column("login", sa.String(200), unique=True, nullable=False),
#     sa.Column("email", sa.String(200), unique=True, nullable=False),
#     sa.Column("password", sa.String(10), nullable=False),
#     sa.Column("is_superuser", sa.Boolean, nullable=False),
#     sa.Column("password", sa.String(10), nullable=False),
#     sa.Column("avatar_url", sa.Text),
#     sa.Column(
#         "gender",
#         gender_enum,
#         server_default=UserGender.none.value,
#     ),
# )


users = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column(
        "login", sa.VARCHAR(length=256), autoincrement=False, nullable=False
    ),
    sa.Column(
        "passwd", sa.VARCHAR(length=256), autoincrement=False, nullable=False
    ),
    sa.Column(
        "is_superuser",
        sa.BOOLEAN(),
        server_default=sa.text("false"),
        autoincrement=False,
        nullable=False,
    ),
    sa.Column(
        "disabled",
        sa.BOOLEAN(),
        server_default=sa.text("false"),
        autoincrement=False,
        nullable=False,
    ),
    sa.Column(
        "gender",
        gender_enum,
        server_default=UserGender.none.value,
    ),
    sa.PrimaryKeyConstraint("id", name="user_pkey"),
    sa.UniqueConstraint("login", name="user_login_key"),
)

permissions = sa.Table(
    "permissions",
    metadata,
    sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column(
        "perm_name", sa.VARCHAR(length=64), autoincrement=False, nullable=False
    ),
    sa.ForeignKeyConstraint(
        ["user_id"],
        ["users.id"],
        name="user_permission_fkey",
        ondelete="CASCADE",
    ),
    sa.PrimaryKeyConstraint("id", name="permission_pkey"),
)
