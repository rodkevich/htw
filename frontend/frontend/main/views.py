from typing import Dict

import aiohttp_jinja2
import markdown2
from aiohttp import web

from frontend.constants import PROJECT_DIR


@aiohttp_jinja2.template('index.html')
async def index(request: web.Request) -> Dict[str, str]:
    with open(PROJECT_DIR / 'README.md') as f:
        text = markdown2.markdown(f.read())

    return {"text": text}


@aiohttp_jinja2.template('login.html')
async def login(request: web.Request):
    return


@aiohttp_jinja2.template('base.html')
async def base(request: web.Request):
    pass


@aiohttp_jinja2.template('auth.html')
async def auth(request: web.Request):
    return {"text": "Иди на хуй"}
