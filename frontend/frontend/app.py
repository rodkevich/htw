import base64
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, List, Optional

import aiohttp_security
import aiohttp_session
import aiopg.sa
import aioredis
import click
import psycopg2
from aiohttp import web
from aiohttp_jinja2 import setup as j2_setup
from aiohttp_security import SessionIdentityPolicy
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session.redis_storage import RedisStorage
from aioredis import Redis
from cryptography import fernet
from jinja2 import FileSystemLoader as J2_fs_loader

from frontend.db_auth import DBAuthorizationPolicy
from frontend.middlewares import setup_middlewares
from frontend.routes import init_routes
from frontend.utils.common import init_config

path = Path(__file__).parent


def init_jinja2(app: web.Application) -> None:
    """
    Initialize jinja2 template for application.
    """
    j2_setup(app, loader=J2_fs_loader(str(path / "templates")))


async def database(app: web.Application) -> AsyncGenerator[None, None]:
    """
    A function that, when the server is started, connects to postgresql,
    and after stopping it breaks the connection (after yield)
    """
    config = app["config"]["postgres"]

    engine = await aiopg.sa.create_engine(**config)
    app["db"] = engine
    click.echo("db")

    yield

    app["db"].close()
    await app["db"].wait_closed()


async def redis(app: web.Application) -> AsyncGenerator[None, None]:
    """
    A function that, when the server is started, connects to redis,
    and after stopping it breaks the connection (after yield)
    """
    config = app["config"]["redis"]

    create_redis = partial(
        aioredis.create_redis, f'redis://{config["host"]}:{config["port"]}'
    )

    sub = await create_redis()
    pub = await create_redis()

    app["redis_sub"] = sub
    app["redis_pub"] = pub
    app["create_redis"] = create_redis
    click.echo("redis")

    yield

    app["redis_sub"].close()
    app["redis_pub"].close()

    await app["redis_sub"].wait_closed()
    await app["redis_pub"].wait_closed()


async def make_redis_pool(app) -> Redis:
    config = app["config"]["redis"]
    click.echo("redis_pool")
    pool = await aioredis.create_redis_pool(
        f'redis://{config["host"]}:{config["port"]}', db=0, timeout=1
    )
    return pool


async def init_app(config: Optional[List[str]] = None) -> web.Application:
    # inbuilt developers server app
    app = web.Application()

    init_config(app, config=config)
    init_jinja2(app)
    init_routes(app)
    setup_middlewares(app)

    # using session cookies as storage
    # secret_key must be 32 url-safe base64-encoded bytes
    # fernet_key = fernet.Fernet.generate_key()
    # secret_key = base64.urlsafe_b64decode(fernet_key)
    # setup session
    # aiohttp_session.setup(
    #     app,
    #     EncryptedCookieStorage(
    #         secret_key,
    #         cookie_name="htw",
    #     ),
    # )

    # Database init:
    config = app["config"]["postgres"]
    connection = psycopg2.connect(**config)
    connection.set_isolation_level(
        psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
    )
    cursor = connection.cursor()
    # Check migrations existence:
    try:
        cursor.execute("SELECT version();")
        record = cursor.fetchone()[0]
        print(f"DB : {record}")

        cursor.execute("SELECT version_num FROM alembic_version;")
        record = cursor.fetchone()[0]
        print(f"Currently active db schema version id : {record}")
    except (Exception, psycopg2.Error) as error:
        print(f"No alembic version available, {error}")
    # input users and permissions:
    try:
        with cursor:
            cursor.execute(
                open("frontend/users/sql/sample_data.sql", "r").read()
            )
            print("Users were added to DB")
    except (Exception, psycopg2.Error):
        print("Users are already in DB")

    # Redis pool :
    pool = await make_redis_pool(app)
    aiohttp_session.setup(app, RedisStorage(pool, cookie_name="htw_redis"))
    # setup Identity and DB policies
    aiohttp_security.setup(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(app["config"]["postgres"]),
    )

    app.cleanup_ctx.extend(
        [
            redis,
            database,
        ]
    )

    return app


async def init_app_gcw(config: Optional[List[str]] = None) -> web.Application:
    # function to run with Gunicorn
    app = web.Application()

    init_jinja2(app)
    init_config(app, config=config)

    pool = await make_redis_pool(app)
    aiohttp_session.setup(app, RedisStorage(pool, cookie_name="htw_redis"))
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)
    # setup session
    aiohttp_session.setup(
        app,
        EncryptedCookieStorage(
            secret_key,
            cookie_name="htw_redis",
        ),
    )

    # setup Identity and DB policies
    aiohttp_security.setup(
        app,
        SessionIdentityPolicy(),
        DBAuthorizationPolicy(app["config"]["postgres"]),
    )

    # setup_middlewares(app)
    init_routes(app)

    app.cleanup_ctx.extend(
        [
            redis,
            database,
        ]
    )

    return app


