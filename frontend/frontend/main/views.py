import aiohttp_jinja2
import click
import markdown2
from aiohttp import web
from aiohttp_security import check_authorized, forget, remember
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
        response = aiohttp_jinja2.render_template(
            "login.html",
            request,
            {"error": "Wrong credentials, dude ..."},
            status=400,
        )
        response.headers["Content-Language"] = "eng"
        return response


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


#
# def handle_json_error(
#     func: Callable[[web.Request], Awaitable[web.Response]]
# ) -> Callable[[web.Request], Awaitable[web.Response]]:
#     async def handler(request: web.Request) -> web.Response:
#         try:
#             return await func(request)
#         except asyncio.CancelledError:
#             raise
#         except Exception as ex:
#             return web.json_response(
#                 {"status": "failed", "reason": str(ex)}, status=400
#             )
#
#     return handler
#
#
# @web.middleware
# async def auth_middleware(request, handler):
#     # выполняется до обработки запроса
#     print("temp plug : Middleware for auth session is called")
#
#     response = await handler(request)
#     return web.Response(status=403, text="Auth error : not today")


# login form
@aiohttp_jinja2.template("login.html")
async def login(request: web.Request):
    session = await get_session(request)
    click.echo(f'Login view : {session}')


async def logout(request):
    await forget(request, response=None)
    raise web.HTTPSeeOther(location="/login")

