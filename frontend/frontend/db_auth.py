import click
import sqlalchemy as sa
from aiohttp_security.abc import AbstractAuthorizationPolicy

from frontend.users import tables


# from passlib.hash import sha256_crypt


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db):
        self.db = db

    async def authorized_userid(self, identity):
        async with self.db.acquire() as conn:
            where = sa.and_(
                tables.users.c.login == identity,
                sa.not_(tables.users.c.disabled),
            )
            query = tables.users.count().where(where)
            ret = await conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False

        async with self.db.acquire() as conn:
            where = sa.and_(
                tables.users.c.login == identity,
                sa.not_(tables.users.c.disabled),
            )
            query = tables.users.select().where(where)
            ret = await conn.execute(query)
            user = await ret.fetchone()
            if user is not None:
                user_id = user[0]
                is_superuser = user[3]
                if is_superuser:
                    return True

                where = tables.permissions.c.user_id == user_id
                query = tables.permissions.select().where(where)
                ret = await conn.execute(query)
                result = await ret.fetchall()
                if ret is not None:
                    for record in result:
                        if record.perm_name == permission:
                            return True

            return False


async def check_credentials(db_engine, username, password):
    async with db_engine.acquire() as conn:
        where = sa.and_(
            tables.users.c.login == username, sa.not_(tables.users.c.disabled)
        )
        query = tables.users.select().where(where)

        ret = await conn.execute(query)
        user = await ret.fetchone()
        if user is not None:
            # hashed = user[2]
            # return sha256_crypt.verify(password, hashed)
            if user[2] == password:
                click.echo("User verified")
                return True
        click.echo("User NOT verified")
        return False
