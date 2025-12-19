import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src.config import USER_SERVICE_URL
from src.dependencies.auth import require_role
from src.utils.http_client import client

router = APIRouter(prefix="/user")

logger = logging.getLogger(__name__)


@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_user(
    request: Request, path: str, payload: Annotated[dict, Depends(require_role("user"))]
) -> Response:
    """Proxy requests to the User Service.

    Args:
        request (Request): The incoming FastAPI request.
        path (str): The path to be appended to the User Service URL.
        payload: Dependency to enforce role-based access control.

    Returns:
        Response: The response from the User Service.

    """
    path = path.rstrip("/")
    query_string = request.url.query
    url = f"{USER_SERVICE_URL}/{path}"
    if query_string:
        url = f"{url}?{query_string}"
    logger.info("Proxying request to User Service: \n%s %s", request.method, url)

    body = await request.body()
    downstream_response = await client.request(
        method=request.method,
        url=url,
        headers=request.headers.raw,
        content=body,
    )

    logger.info(
        "Received response from User Service with content: \n%s",
        downstream_response.content.decode(),
    )
    return Response(
        content=downstream_response.content,
        status_code=downstream_response.status_code,
        headers=dict(downstream_response.headers),
        media_type=downstream_response.headers.get("content-type"),
    )
