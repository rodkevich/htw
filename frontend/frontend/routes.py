import pathlib

from aiohttp import web

from frontend.main.views import auth, index

from frontend.main.views import login

PROJECT_PATH = pathlib.Path(__file__).parent


def init_routes(app: web.Application) -> None:
    add_route = app.router.add_route

    add_route("*", "/", index, name="index")

    add_route("*", "/login", login, name="login")
    add_route("*", "/auth", auth, name="auth")

    # added static dir
    app.router.add_static(
        "/static/",
        path=(PROJECT_PATH / "static"),
        name="static",
        append_version=True,
    )
