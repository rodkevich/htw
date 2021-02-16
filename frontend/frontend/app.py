import base64
from functools import partial
from pathlib import Path
from typing import AsyncGenerator, List, Optional

import aiohttp_jinja2
import aiohttp_security
import aiohttp_session
import aiopg.sa
import aioredis
import click
import jinja2
from aiohttp import web
from aiohttp_security import SessionIdentityPolicy
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_session.redis_storage import RedisStorage
from cryptography import fernet

from frontend.db_auth import DBAuthorizationPolicy
from frontend.middlewares import setup_middlewares
from frontend.routes import init_routes
from frontend.utils.common import init_config

path = Path(__file__).parent


def init_jinja2(app: web.Application) -> None:
    """
    Initialize jinja2 template for application.
    """
    aiohttp_jinja2.setup(
        app, loader=jinja2.FileSystemLoader(str(path / "templates"))
    )


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


async def redis(app: web.Application) -> None:
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

    pool = await make_redis_pool(app)
    aiohttp_session.setup(
        app,
        RedisStorage(
            pool,
            cookie_name="htw_redis"
        )
    )
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


async def make_redis_pool(app):
    config = app["config"]["redis"]
    click.echo("redis_pool")
    pool = await aioredis.create_redis_pool(
        f'redis://{config["host"]}:{config["port"]}', db=0, timeout=1
    )
    return pool


async def init_app_gcw(config: Optional[List[str]] = None) -> web.Application:
    # function to run with Gunicorn
    app = web.Application()

    init_jinja2(app)
    init_config(app, config=config)

    pool = await make_redis_pool(app)
    aiohttp_session.setup(
        app,
        RedisStorage(
            pool,
            cookie_name="htw_redis"
        )
    )
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

    setup_middlewares(app)
    init_routes(app)
    app.cleanup_ctx.extend(
        [
            redis,
            database,
        ]
    )

    return app
