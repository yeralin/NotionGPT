
"""
gpt.py

A module that provides a helper class 'GPT' for working with GPT models using
the OpenAI API. The class includes methods for calculating tokens, constructing
GPT payloads, and sending GPT payloads to the API based on the contents of a
Notion page.
"""
from enum import Enum
from typing import Dict, List, Tuple

import openai
import tiktoken

from notion import Notion


class GPTModel(Enum):
    """
    Enumeration of GPT models with their respective IDs and token limits.
    """

    CHAT_GPT = ("gpt-3.5-turbo", 4096)
    CHAT_GPT_16K = ("gpt-3.5-turbo-16k", 16384)
    GPT_4 = ("gpt-4", 8192)
    GPT_4_32K = ("gpt-4-32k", 32768)

    def __new__(cls, id: str, limit: int):
        """Create custom Enum object"""
        obj = object.__new__(cls)
        obj.id = id
        obj.limit = limit
        return obj


class GPT:
    """
    A helper class for working with GPT models using the OpenAI API.
    The class includes methods for calculating tokens, constructing GPT payloads,
    and sending GPT payloads to the API based on the contents of a Notion page.
    """

    def __init__(self, notion: Notion):
        self.notion = notion

    def _calculate_tokens(self, msg: Dict[str, str], model: GPTModel = GPTModel.CHAT_GPT) -> int:
        """
        Calculate the number of tokens required for a given message.

        Args:
            msg: The message content with role (e.g., {'role': 'user', 'content': 'Hello'})
            model: The GPT model to calculate tokens for. Defaults to GPTModel.CHAT_GPT.

        Returns:
            int: The number of tokens required for the given message.
        """
        try:
            encoding = tiktoken.encoding_for_model(model.id)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model.id == "gpt-3.5-turbo":
            num_tokens = 4
            for key, value in msg.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens -= 1
            num_tokens += 2
            return num_tokens
        else:
            raise NotImplementedError(
                f"calculate_tokens() is not presently implemented for model {model}"
            )


    def construct_gpt_payload(self, blocks: List[Dict], command: str) -> Tuple[List[Dict[str, str]], GPTModel]:
        """
        Construct the payload for GPT conversation given a Notion page ID.

        Args:
            page_id: The ID of the Notion page containing the conversation.
            command: User command to act upon the fetched Notion content

        Returns:
            A tuple containing the list of messages and the GPT model.
        """
        messages = []
        tokens = 0
        model = GPTModel.CHAT_GPT
        # Fetches history in reverse order
        for block in reversed(blocks):
            content = self.notion.get_plain_text_from_block(block)
            if not content:
                continue
            entry = {"role": "user", "content": content}
            tokens += self._calculate_tokens(entry)
            if tokens > model.limit:
                break
            messages.insert(0, entry)
        messages.append({
            "role": "user",
            "content": command
        })
        return messages, model


    def send_gpt_payload(self, messages: List[Dict[str, str]], model: GPTModel):
        """
        Send a list of message payloads to the GPT API.

        Args:
            messages: List of message payloads (e.g., [{'role': 'user', 'content': 'Hello'}])
            model: The GPT model to send the payloads to.

        Returns:
            str: The assistant's response from the GPT API.
        """
        response = openai.ChatCompletion.create(
            model=model.id,
            messages=messages
        )
        assistant_response = response['choices'][0]['message']['content']
        return assistant_response
