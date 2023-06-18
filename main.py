import os

from dotenv import load_dotenv; load_dotenv() # Fetch env vars first
from flask import Flask, jsonify, request
from notion_client import Client

from gpt import GPT
from notion import Notion


app = Flask(__name__)
notion_client = Client(auth=os.environ["NOTION_TOKEN"])
notion = Notion(notion_client)
gpt = GPT(notion)

@app.route('/notion-gpt', methods=['POST'])
def respond():
    """
    A Flask API endpoint that processes a Notion page with a given page_id,
    simulates a conversation with GPT models using the page's content and a provided command,
    and adds the assistant's response as a new block in the same Notion page.

    The endpoint expects a POST request with a JSON payload containing 'page_id' and 'command'.
    Example payload: {"page_id": "<your_notion_page_id>", "command": "tell me a joke"}
    """
    data = request.get_json()

    # Extract the page_id and command from the request data
    page_id = data.get("page_id")
    command = data.get("command")

    if not page_id or not command:
        return jsonify({"error": "Please provide both page_id and command."}), 400

    # Process the Notion page
    blocks = notion.fetch_page_blocks(page_id)

    # Construct GPT payload
    messages, model = gpt.construct_gpt_payload(blocks, command)

    # Send GPT payload and get a response
    assistant_response = gpt.send_gpt_payload(messages, model)

    # Add assistant's response as a block to the Notion page
    notion.add_block_to_page(page_id, assistant_response)

    # Return the assistant's response
    return jsonify({"response": assistant_response})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")
