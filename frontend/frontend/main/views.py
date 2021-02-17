import aiohttp_jinja2
import click
import markdown2
from aiohttp import web
from aiohttp_security.api import IDENTITY_KEY
from aiohttp_session import get_session

from frontend.constants import PROJECT_DIR


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
