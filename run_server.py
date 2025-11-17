
import logging
import os
import sys

import anyio
from dotenv import load_dotenv
from mcp.server.stdio import stdio_server

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import (
    ApiKeyConfig,
    AuthConfig,
    AuthType,
    BasicAuthConfig,
    OAuthConfig,
    ServerConfig,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_config_from_env() -> ServerConfig:
    """
    Create server configuration from environment variables.

    Returns:
        ServerConfig: Server configuration.

    Raises:
        ValueError: If required configuration is missing.
    """
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    if not instance_url:
        raise ValueError("SERVICENOW_INSTANCE_URL environment variable not set.")

    auth_type_str = os.getenv("SERVICENOW_AUTH_TYPE", "basic").lower()
    auth_type = AuthType(auth_type_str)
    
    final_auth_config: AuthConfig

    if auth_type == AuthType.BASIC:
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        if not username or not password:
            raise ValueError("SERVICENOW_USERNAME and SERVICENOW_PASSWORD must be set for basic auth.")
        basic_cfg = BasicAuthConfig(username=username, password=password)
        final_auth_config = AuthConfig(type=auth_type, basic=basic_cfg)

    elif auth_type == AuthType.OAUTH:
        client_id = os.getenv("SERVICENOW_CLIENT_ID")
        client_secret = os.getenv("SERVICENOW_CLIENT_SECRET")
        username = os.getenv("SERVICENOW_USERNAME")
        password = os.getenv("SERVICENOW_PASSWORD")
        token_url = os.getenv("SERVICENOW_TOKEN_URL", f"{instance_url}/oauth_token.do")
        if not client_id or not client_secret or not username or not password:
            raise ValueError("Client ID, client secret, username, and password are required for OAuth password grant.")
        oauth_cfg = OAuthConfig(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            token_url=token_url,
        )
        final_auth_config = AuthConfig(type=auth_type, oauth=oauth_cfg)

    elif auth_type == AuthType.API_KEY:
        api_key = os.getenv("SERVICENOW_API_KEY")
        api_key_header = os.getenv("SERVICENOW_API_KEY_HEADER", "X-ServiceNow-API-Key")
        if not api_key:
            raise ValueError("API key is required for API key authentication.")
        api_key_cfg = ApiKeyConfig(api_key=api_key, header_name=api_key_header)
        final_auth_config = AuthConfig(type=auth_type, api_key=api_key_cfg)
    else:
        raise ValueError(f"Unsupported authentication type: {auth_type_str}")

    script_execution_api_resource_path = os.getenv("SCRIPT_EXECUTION_API_RESOURCE_PATH")
    if not script_execution_api_resource_path:
        logger.warning("Script execution API resource path not set. ExecuteScriptInclude tool may fail.")

    return ServerConfig(
        instance_url=instance_url,
        auth=final_auth_config,
        debug=os.getenv("SERVICENOW_DEBUG", "false").lower() == "true",
        timeout=int(os.getenv("SERVICENOW_TIMEOUT", "30")),
        script_execution_api_resource_path=script_execution_api_resource_path,
    )


async def arun_server(server_instance):
    """Runs the given MCP server instance using stdio transport."""
    logger.info("Starting server with stdio transport...")
    async with stdio_server() as streams:
        init_options = server_instance.create_initialization_options()
        await server_instance.run(streams[0], streams[1], init_options)
    logger.info("Stdio server finished.")


def main():
    """Main entry point for the CLI."""
    load_dotenv()

    try:
        debug_mode = os.getenv("SERVICENOW_DEBUG", "false").lower() == "true"
        if debug_mode:
            logging.getLogger().setLevel(logging.DEBUG)
            logger.info("Debug logging enabled.")
        else:
            logging.getLogger().setLevel(logging.INFO)

        config = create_config_from_env()
        logger.info(f"Initializing ServiceNow MCP server for instance: {config.instance_url}")

        mcp_controller = ServiceNowMCP(config)
        server_to_run = mcp_controller.start()
        anyio.run(arun_server, server_to_run)

    except ValueError as e:
        logger.error(f"Configuration or runtime error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error starting or running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
