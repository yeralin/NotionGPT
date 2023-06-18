"""
notion.py

A module that provides a helper class 'Notion' for working with the Notion API
using the notion-client library. It encapsulates functionality for fetching
page blocks, extracting plain text from blocks, and adding blocks to a page.
"""
import re
from typing import Dict, List


class Notion:
    """
    A helper class for working with the Notion API using the notion-client library.
    It encapsulates functionality for fetching page blocks, extracting plain text
    from blocks, and adding blocks to a page.
    """

    def __init__(self, notion_client):
        self.notion_client = notion_client

    def get_plain_text_from_block(self, block: Dict) -> str:
        """
        Extracts plain text from a block string.

        Args:
            block: The block string to extract plain text from.

        Returns:
            str: The extracted plain text.
        """
        plain_text_pattern = r"'plain_text':\s?'([^']*)'"
        match = re.search(plain_text_pattern, str(block))
        return match.group(1) if match else None


    def fetch_page_blocks(self, page_id: str) -> List[Dict]:
        """
        Fetch the list of block children of a given Notion page.

        Args:
            page_id (str): The ID of the Notion page.

        Returns:
            The list of block children.
        """
        # Check if the provided page_id is not empty
        if not page_id:
            raise ValueError("Page ID is required.")

        # Fetch the list of block children of the given Notion page
        response = self.notion_client.blocks.children.list(page_id)

        # Return the block list
        return response.get("results")


    def add_block_to_page(self, page_id: str, content: str):
        """
        Add a block of text to a Notion page.

        Args:
            page_id (str): The ID of the Notion page to add the block to.
            content (str): The content to be added to the Notion page.
        """

        new_block = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]},
        }

        self.notion_client.blocks.children.append(page_id, children=[new_block])
