#!/usr/bin/python
import aiohttp_jinja2
from aiohttp import web
from aiohttp_security import forget, remember
from aiohttp_session import get_session

from frontend.db_auth import check_credentials


async def auth(request: web.Request):
    response = web.HTTPFound("/")
    form = await request.post()
    login = form.get("username")
    password = form.get("password")
    db_engine = request.app["db"]
    if await check_credentials(db_engine, login, password):
        await remember(request, response, login)
        session = await get_session(request)
        import click

        click.echo(session)
        raise response

    else:
        response = aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Wrong credentials, dude ..."},
            status=400,
        )
        response.headers["Content-Language"] = "eng"
        return response


async def logout(request):
    await forget(request, response=None)
    raise web.HTTPSeeOther(location="/login")
