"""empty message

Revision ID: 3395a3ed1f68
Revises: 
Create Date: 2021-02-14 15:44:29.939691

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3395a3ed1f68'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('login', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('passwd', sa.VARCHAR(length=256), autoincrement=False, nullable=False),
    sa.Column('is_superuser', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('disabled', sa.BOOLEAN(), server_default=sa.text('false'), autoincrement=False, nullable=False),
    sa.Column('gender', postgresql.ENUM('women', 'male', 'none', name='usergender'), server_default='none', nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey'),
    sa.UniqueConstraint('login', name='user_login_key')
    )
    op.create_table('permissions',
    sa.Column('id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('perm_name', sa.VARCHAR(length=64), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='user_permission_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='permission_pkey')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('permissions')
    op.drop_table('users')
    # ### end Alembic commands ###
