# HTTP Request MCP Server

A Model Context Protocol server that provides HTTP request capabilities. This server enables LLMs to make HTTP requests using GET, POST, PUT, PATCH, and DELETE methods.

> [!CAUTION]
> This server can access local/internal IP addresses and may represent a security risk. Exercise caution when using this MCP server to ensure this does not expose any sensitive data.

## Available Tools

- `http_get` - Makes an HTTP GET request to retrieve data
  - `url` (string, required): URL to send GET request to
  - `headers` (object, optional): HTTP headers to include in the request
  - `params` (object, optional): Query parameters to include in the request

- `http_post` - Makes an HTTP POST request to create new resources
  - `url` (string, required): URL to send POST request to
  - `headers` (object, optional): HTTP headers to include in the request
  - `body` (string or object, optional): Request body (sent as JSON if object)

- `http_put` - Makes an HTTP PUT request to update/replace resources
  - `url` (string, required): URL to send PUT request to
  - `headers` (object, optional): HTTP headers to include in the request
  - `body` (string or object, optional): Request body (sent as JSON if object)

- `http_patch` - Makes an HTTP PATCH request to partially update resources
  - `url` (string, required): URL to send PATCH request to
  - `headers` (object, optional): HTTP headers to include in the request
  - `body` (string or object, optional): Request body (sent as JSON if object)

- `http_delete` - Makes an HTTP DELETE request to delete resources
  - `url` (string, required): URL to send DELETE request to
  - `headers` (object, optional): HTTP headers to include in the request

## Installation

### Using uv (recommended)

When using [`uv`](https://docs.astral.sh/uv/) no specific installation is needed. We will use [`uvx`](https://docs.astral.sh/uv/guides/tools/) to directly run *mcp-server-http-request*.

### Using PIP

Alternatively you can install `mcp-server-http-request` via pip:

```bash
pip install mcp-server-http-request
```

After installation, you can run it as a script using:

```bash
python -m mcp_server_http_request
```

## Configuration

### Configure for Claude.app

Add to your Claude settings:

<details>
<summary>Using uvx</summary>

```json
{
  "mcpServers": {
    "http-request": {
      "command": "uvx",
      "args": ["mcp-server-http-request"]
    }
  }
}
```
</details>

<details>
<summary>Using pip installation</summary>

```json
{
  "mcpServers": {
    "http-request": {
      "command": "python",
      "args": ["-m", "mcp_server_http_request"]
    }
  }
}
```
</details>

### Customization - User-agent

By default, the server uses the user-agent:
```
ModelContextProtocol/1.0 (HTTP-Request; +https://github.com/modelcontextprotocol/servers)
```

This can be customized by adding the argument `--user-agent=YourUserAgent` to the `args` list in the configuration.

### Customization - Proxy

The server can be configured to use a proxy by using the `--proxy-url` argument.

## Usage Examples

### GET Request
```json
{
  "url": "https://api.example.com/users",
  "params": {
    "page": "1",
    "limit": "10"
  },
  "headers": {
    "Authorization": "Bearer token123"
  }
}
```

### POST Request
```json
{
  "url": "https://api.example.com/users",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
  },
  "body": {
    "name": "John Doe",
    "email": "john@example.com"
  }
}
```

### PUT Request
```json
{
  "url": "https://api.example.com/users/123",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
  },
  "body": {
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

### PATCH Request
```json
{
  "url": "https://api.example.com/users/123",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer token123"
  },
  "body": {
    "email": "newemail@example.com"
  }
}
```

### DELETE Request
```json
{
  "url": "https://api.example.com/users/123",
  "headers": {
    "Authorization": "Bearer token123"
  }
}
```

## Debugging

You can use the MCP inspector to debug the server. For uvx installations:

```bash
npx @modelcontextprotocol/inspector uvx mcp-server-http-request
```

Or if you've installed the package in a specific directory or are developing on it:

```bash
cd path/to/mcp-server-http-request
npx @modelcontextprotocol/inspector uv run mcp-server-http-request
```

## Development

To set up for development:

```bash
# Clone the repository
git clone <repository-url>
cd mcp-server-http-request

# Install dependencies
uv pip install -e .
```

## License

mcp-server-http-request is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License. For more details, please see the LICENSE file in the project repository.
