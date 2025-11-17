
import os
import uvicorn
from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.server_sse import create_starlette_app
from servicenow_mcp.utils.config import ServerConfig, AuthConfig, AuthType, BasicAuthConfig, OAuthConfig

def main():
    """
    Starts the ServiceNow MCP SSE server by reading configuration
    from environment variables.
    """
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    auth_type_str = os.getenv("SERVICENOW_AUTH_TYPE", "basic").lower()
    debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"

    if not instance_url:
        raise ValueError("SERVICENOW_INSTANCE_URL environment variable not set.")

    auth_config = None
    if auth_type_str == "basic":
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        if not username or not password:
            raise ValueError("SERVICENOW_USERNAME and SERVICENOW_PASSWORD must be set for basic auth.")
        auth_config = AuthConfig(
            type=AuthType.BASIC,
            config=BasicAuthConfig(username=username, password=password)
        )
    elif auth_type_str == "oauth":
        # This assumes you have client_id, client_secret, and token_url in the env
        client_id = os.getenv("SERVICENOW_CLIENT_ID")
        client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")
        # token_url is often derived from instance_url, but can be explicit
        token_url = os.getenv("SERVICENOW_TOKEN_URL", f"{instance_url}/oauth_token.do")
        if not client_id or not client_secret:
            raise ValueError("SERVICENOW_CLIENT_ID and SERVICENOW_CLIENT_SECRET must be set for oauth.")
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        if not username or not password:
            raise ValueError("SERVICENOW_USERNAME and SERVICENOW_PASSWORD must be set for oauth.")
        auth_config = AuthConfig(
            type=AuthType.OAUTH,
            config=OAuthConfig(client_id=client_id, client_secret=client_secret, username=username, password=password, token_url=token_url)
        )
    else:
        raise ValueError(f"Unsupported SERVICENOW_AUTH_TYPE: {auth_type_str}")

    # Create server configuration
    config = ServerConfig(
        instance_url=instance_url,
        auth=auth_config,
        debug=debug_mode,
    )

    # Create ServiceNow MCP server instance
    servicenow_mcp = ServiceNowMCP(config)

    # Create Starlette app with SSE transport
    app = create_starlette_app(servicenow_mcp, debug=debug_mode)

    # Start the web server
    print(f"Starting ServiceNow MCP server for instance: {instance_url}")
    print(f"Authentication type: {auth_type_str}")
    print(f"Debug mode: {debug_mode}")
    uvicorn.run(app, host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
