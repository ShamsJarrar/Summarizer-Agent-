from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import json

mcp = FastMCP("retrieve", host="0.0.0.0", port=8000)

def save_to_file(content):
    FILE_NAME = 'retrieved_result.json'
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r") as f:
            data = json.load(f)
    else:
        data = []
    data.extend(content)
    with open(FILE_NAME, "w") as f:
        json.dump(data, f, indent=2)



@mcp.tool()
def retrieve_information(query: str) -> str:
    """
    Searches the web for information related to the query to help with the summarization, providing real time data.

    Args:
        query: topic to search for

    Returns:
        confirmation that search results are saved to retrieved_result.json
    """
    try:
        load_dotenv()
        client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        search = client.search(query, max_results=3, search_depth="advanced")

        content = [
            {
                'title': s['title'],
                'content': s['content']
            }
            for s in search['results']
        ]

        save_to_file(content)
        return "Results saved to retrieved_result.json"
    except Exception as e:
        return f"[ERROR] Tool failed during execution: {e}"


if __name__ == "__main__":
    mcp.run(transport='streamable-http')