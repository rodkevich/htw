import aiohttp_jinja2
import click
import markdown2
from aiohttp import web
from aiohttp_security import forget, remember
from aiohttp_security.api import IDENTITY_KEY
from aiohttp_session import get_session

from frontend.constants import PROJECT_DIR
from frontend.db_auth import check_credentials


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request):
    session = await get_session(request)
    click.echo(session)
    if session:
        with open(PROJECT_DIR / "README.md") as f:
            text = markdown2.markdown(f.read())
            return {"text": text}
    else:
        raise web.HTTPSeeOther(location="/login")


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


# login form
@aiohttp_jinja2.template("login.html")
async def login(request: web.Request):
    session = await get_session(request)
    click.echo(session)
    click.echo(request.config_dict.get(IDENTITY_KEY))
    # await check_authorized(request)
    if session:
        with open(PROJECT_DIR / "README.md") as f:
            text = markdown2.markdown(f.read())
            return {"text": text}
    else:
        response = aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Authorize, dude ..."},
            status=400,
        )
        response.headers["Content-Language"] = "eng"
        return response


async def logout(request):
    await forget(request, response=None)
    raise web.HTTPSeeOther(location="/login")
