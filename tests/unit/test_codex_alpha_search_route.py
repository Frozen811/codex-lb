from fastapi.routing import APIRoute

from app.modules.proxy.api import router, v1_router


def test_codex_alpha_search_route_is_post_only() -> None:
    routes = [
        route
        for route in router.routes
        if isinstance(route, APIRoute) and route.path == "/backend-api/codex/alpha/search"
    ]

    assert len(routes) == 1
    assert routes[0].methods == {"POST"}


def test_codex_alpha_search_v1_route_is_post_only() -> None:
    routes = [
        route
        for route in v1_router.routes
        if isinstance(route, APIRoute) and route.path == "/v1/alpha/search"
    ]

    assert len(routes) == 1
    assert routes[0].methods == {"POST"}

