import aiohttp_jinja2
import markdown2
from aiohttp import web

from frontend.constants import PROJECT_DIR
from frontend.db_auth import check_credentials


@aiohttp_jinja2.template("index.html")
async def index(request: web.Request):
    with open(PROJECT_DIR / "README.md") as f:
        text = markdown2.markdown(f.read())
        return {"text": text}


async def auth(request: web.Request):
    form = await request.post()
    login = form.get("username")
    password = form.get("password")

    db_engine = request.app["db"]
    if await check_credentials(db_engine, login, password):
        redirect_response = web.HTTPFound("/")
        """
        Bug in 3.7 aiohttp
        """
        # from aiohttp_security import remember
        # await remember(request, redirect_response, login)
        raise redirect_response

    else:
        response = aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Wrong credentials, dude ..."},
            status=400,
        )
        response.headers["Content-Language"] = "eng"
        return response


@aiohttp_jinja2.template("base.html")
async def base(request: web.Request):
    pass


@aiohttp_jinja2.template("login.html")
async def login(request: web.Request):
    pass
