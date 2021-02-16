# middlewares.py
import aiohttp_jinja2
from aiohttp import web


async def handle_404(request):
    return aiohttp_jinja2.render_template("404.html", request, {})


async def handle_500(request):
    return aiohttp_jinja2.render_template("500.html", request, {})


def create_error_middleware(overrides):
    @web.middleware
    async def error_middleware(request, handler):

        try:
            response = await handler(request)

            override = overrides.get(response.status)
            if override:
                return await override(request)

            return response

        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise

    return error_middleware


def setup_middlewares(app):
    error_middleware = create_error_middleware(
        {404: handle_404, 500: handle_500}
    )
    app.middlewares.append(error_middleware)


# -------------------------------------------------------------------------
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
