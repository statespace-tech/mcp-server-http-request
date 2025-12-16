import json
from typing import Annotated, Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.shared.exceptions import McpError
from mcp.types import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    ErrorData,
    TextContent,
    Tool,
)
from pydantic import AnyUrl, BaseModel, Field

DEFAULT_USER_AGENT = "ModelContextProtocol/1.0 (HTTP-Request; +https://github.com/modelcontextprotocol/servers)"


class GetRequest(BaseModel):
    """Parameters for making a GET request."""

    url: Annotated[AnyUrl, Field(description="URL to send GET request to")]
    headers: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional HTTP headers to include in the request as a JSON object",
        ),
    ]
    params: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional query parameters to include in the request as a JSON object",
        ),
    ]


class PostRequest(BaseModel):
    """Parameters for making a POST request."""

    url: Annotated[AnyUrl, Field(description="URL to send POST request to")]
    headers: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional HTTP headers to include in the request as a JSON object",
        ),
    ]
    body: Annotated[
        str | dict[str, Any] | None,
        Field(
            default=None,
            description="Optional request body. Can be a JSON object or a string. If a dict is provided, it will be sent as JSON",
        ),
    ]


class PutRequest(BaseModel):
    """Parameters for making a PUT request."""

    url: Annotated[AnyUrl, Field(description="URL to send PUT request to")]
    headers: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional HTTP headers to include in the request as a JSON object",
        ),
    ]
    body: Annotated[
        str | dict[str, Any] | None,
        Field(
            default=None,
            description="Optional request body. Can be a JSON object or a string. If a dict is provided, it will be sent as JSON",
        ),
    ]


class PatchRequest(BaseModel):
    """Parameters for making a PATCH request."""

    url: Annotated[AnyUrl, Field(description="URL to send PATCH request to")]
    headers: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional HTTP headers to include in the request as a JSON object",
        ),
    ]
    body: Annotated[
        str | dict[str, Any] | None,
        Field(
            default=None,
            description="Optional request body. Can be a JSON object or a string. If a dict is provided, it will be sent as JSON",
        ),
    ]


class DeleteRequest(BaseModel):
    """Parameters for making a DELETE request."""

    url: Annotated[AnyUrl, Field(description="URL to send DELETE request to")]
    headers: Annotated[
        dict[str, str] | None,
        Field(
            default=None,
            description="Optional HTTP headers to include in the request as a JSON object",
        ),
    ]


async def make_http_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: str | dict[str, Any] | None = None,
    params: dict[str, str] | None = None,
    user_agent: str = DEFAULT_USER_AGENT,
    proxy_url: str | None = None,
) -> tuple[int, dict[str, str], str]:
    """
    Make an HTTP request and return status code, headers, and response body.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        url: Target URL
        headers: Optional request headers
        body: Optional request body (string or dict)
        params: Optional query parameters
        user_agent: User agent string
        proxy_url: Optional proxy URL

    Returns:
        Tuple of (status_code, response_headers, response_body)
    """
    from httpx import AsyncClient, HTTPError

    # Prepare headers
    request_headers = {"User-Agent": user_agent}
    if headers:
        request_headers.update(headers)

    # Prepare body
    request_body = None
    if body is not None:
        if isinstance(body, dict):
            request_body = json.dumps(body)
            if "Content-Type" not in request_headers:
                request_headers["Content-Type"] = "application/json"
        else:
            request_body = body

    async with AsyncClient(proxies=proxy_url, timeout=30) as client:
        try:
            response = await client.request(
                method=method,
                url=url,
                headers=request_headers,
                content=request_body,
                params=params,
                follow_redirects=True,
            )
        except HTTPError as e:
            raise McpError(
                ErrorData(
                    code=INTERNAL_ERROR,
                    message=f"Failed to make {method} request to {url}: {e!r}",
                )
            )

    # Get response headers as dict
    response_headers = dict(response.headers)

    # Get response body
    try:
        response_body = response.text
    except Exception:
        response_body = "<binary or non-text content>"

    return response.status_code, response_headers, response_body


def format_response(
    method: str, url: str, status_code: int, headers: dict[str, str], body: str
) -> str:
    """Format the HTTP response for display."""
    headers_str = "\n".join(f"{k}: {v}" for k, v in headers.items())
    return f"""HTTP {method} request to {url}

Status Code: {status_code}

Response Headers:
{headers_str}

Response Body:
{body}"""


async def serve(
    custom_user_agent: str | None = None,
    proxy_url: str | None = None,
) -> None:
    """Run the HTTP request MCP server.

    Args:
        custom_user_agent: Optional custom User-Agent string to use for requests
        proxy_url: Optional proxy URL to use for requests
    """
    server = Server("mcp-http-request")
    user_agent = custom_user_agent or DEFAULT_USER_AGENT

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="http_get",
                description="Makes an HTTP GET request to the specified URL. Use this to retrieve data from an API or web server.",
                inputSchema=GetRequest.model_json_schema(),
            ),
            Tool(
                name="http_post",
                description="Makes an HTTP POST request to the specified URL with an optional body. Use this to create new resources or submit data to an API.",
                inputSchema=PostRequest.model_json_schema(),
            ),
            Tool(
                name="http_put",
                description="Makes an HTTP PUT request to the specified URL with an optional body. Use this to update or replace existing resources in an API.",
                inputSchema=PutRequest.model_json_schema(),
            ),
            Tool(
                name="http_patch",
                description="Makes an HTTP PATCH request to the specified URL with an optional body. Use this to partially update existing resources in an API.",
                inputSchema=PatchRequest.model_json_schema(),
            ),
            Tool(
                name="http_delete",
                description="Makes an HTTP DELETE request to the specified URL. Use this to delete resources from an API.",
                inputSchema=DeleteRequest.model_json_schema(),
            ),
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "http_get":
            try:
                args = GetRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            url = str(args.url)
            status_code, headers, body = await make_http_request(
                method="GET",
                url=url,
                headers=args.headers,
                params=args.params,
                user_agent=user_agent,
                proxy_url=proxy_url,
            )
            response_text = format_response("GET", url, status_code, headers, body)
            return [TextContent(type="text", text=response_text)]

        elif name == "http_post":
            try:
                args = PostRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            url = str(args.url)
            status_code, headers, body = await make_http_request(
                method="POST",
                url=url,
                headers=args.headers,
                body=args.body,
                user_agent=user_agent,
                proxy_url=proxy_url,
            )
            response_text = format_response("POST", url, status_code, headers, body)
            return [TextContent(type="text", text=response_text)]

        elif name == "http_put":
            try:
                args = PutRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            url = str(args.url)
            status_code, headers, body = await make_http_request(
                method="PUT",
                url=url,
                headers=args.headers,
                body=args.body,
                user_agent=user_agent,
                proxy_url=proxy_url,
            )
            response_text = format_response("PUT", url, status_code, headers, body)
            return [TextContent(type="text", text=response_text)]

        elif name == "http_patch":
            try:
                args = PatchRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            url = str(args.url)
            status_code, headers, body = await make_http_request(
                method="PATCH",
                url=url,
                headers=args.headers,
                body=args.body,
                user_agent=user_agent,
                proxy_url=proxy_url,
            )
            response_text = format_response("PATCH", url, status_code, headers, body)
            return [TextContent(type="text", text=response_text)]

        elif name == "http_delete":
            try:
                args = DeleteRequest(**arguments)
            except ValueError as e:
                raise McpError(ErrorData(code=INVALID_PARAMS, message=str(e)))

            url = str(args.url)
            status_code, headers, body = await make_http_request(
                method="DELETE",
                url=url,
                headers=args.headers,
                user_agent=user_agent,
                proxy_url=proxy_url,
            )
            response_text = format_response("DELETE", url, status_code, headers, body)
            return [TextContent(type="text", text=response_text)]

        else:
            raise McpError(
                ErrorData(code=INVALID_PARAMS, message=f"Unknown tool: {name}")
            )

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)
