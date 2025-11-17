"""
Tests for the ServiceNow MCP server integration with catalog functionality.
"""

import unittest
from unittest.mock import MagicMock, patch

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.tools.catalog_tools import (
    GetCatalogItemParams,
    ListCatalogCategoriesParams,
    ListCatalogItemsParams,
)
from servicenow_mcp.tools.catalog_tools import (
    get_catalog_item as get_catalog_item_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_categories as list_catalog_categories_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_items as list_catalog_items_tool,
)


class TestServerCatalog(unittest.TestCase):
    """Test cases for the server integration with catalog functionality."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "instance_url": "https://example.service-now.com",
            "auth": {
                "type": "basic",
                "basic": {
                    "username": "admin",
                    "password": "password",
                },
            },
        }

        # Create a mock server
        self.server = ServiceNowMCP(self.config)

        # Mock the FastMCP server
        self.server.mcp_server = MagicMock()
        self.server.mcp_server.resource = MagicMock()
        self.server.mcp_server.tool = MagicMock()












if __name__ == "__main__":
    unittest.main() 