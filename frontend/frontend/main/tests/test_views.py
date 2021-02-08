from pytest_aiohttp import aiohttp_client


async def test_view(client: aiohttp_client) -> None:
    resp = await client.get('/')
    assert resp.status == 200
    assert 'Prykhodzka learns ho to web' in await resp.text()


async def test_login(client: aiohttp_client) -> None:
    resp = await client.get('/login')
    assert resp.status == 200
