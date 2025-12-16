from .server import serve


def main():
    """MCP HTTP Request Server - HTTP request functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="Give a model the ability to make HTTP requests (GET, POST, PUT, PATCH, DELETE)"
    )
    parser.add_argument("--user-agent", type=str, help="Custom User-Agent string")
    parser.add_argument("--proxy-url", type=str, help="Proxy URL to use for requests")

    args = parser.parse_args()
    asyncio.run(serve(args.user_agent, args.proxy_url))


if __name__ == "__main__":
    main()
