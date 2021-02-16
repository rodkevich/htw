import pathlib

from aiohttp import web

from frontend.main.views import auth, index, login, logout

PROJECT_PATH = pathlib.Path(__file__).parent


# Init routes in started application
def init_routes(app: web.Application) -> None:
    add_route = app.router.add_route

    add_route("GET", "/", index, name="index")
    # login
    add_route("GET", "/login", login, name="login")
    add_route("POST", "/login", auth, name="login")
    add_route("GET", "/logout", logout, name="logout")

    # added static dir
    app.router.add_static(
        "/static/",
        path=(PROJECT_PATH / "static"),
        name="static",
        append_version=True,
    )
