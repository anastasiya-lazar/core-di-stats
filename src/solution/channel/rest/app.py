import asyncio

from aiohttp import web
from config import HEALTH_CHECK_PORT
from core.impl.health_check import HealthCheckState

from bst_core.shared.logger import get_logger

routes = web.RouteTableDef()

logger = get_logger(__name__)


@routes.get("/health_check")
async def check(request):
    await HealthCheckState().update()
    response = {
        key: value.__dict__ for key, value in HealthCheckState().public_state.items()
    }

    status_code = 200
    healthy = all(map(lambda state: state["healthy"], response.values()))
    logger.info(response)
    if not healthy:
        status_code = 500
    return web.json_response(response, status=status_code)


app = web.Application()
app.add_routes(routes)


async def run_app(loop):
    web.run_app(app, port=HEALTH_CHECK_PORT, loop=loop)


def run_non_block(loop):
    runner = web.AppRunner(app)
    loop.run_until_complete(runner.setup())
    site = web.TCPSite(runner, port=HEALTH_CHECK_PORT)
    return site


if __name__ == "__main__":
    asyncio.run(run_app(asyncio.get_event_loop()))
