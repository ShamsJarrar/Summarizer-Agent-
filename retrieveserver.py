from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv
import os


mcp = FastMCP("retrieve")

@mcp.tool()
def retrieve_information(query: str) -> list:
    """
    Searches the web for information related to the query to help with the summarization, providing real time data.

    Args:
        query: topic to search for

    Returns:
        list containing title and content of several webpages related to the topic
    """
    load_dotenv()
    client = TavilyClient(api_key=os.getenv("Tavily_API_KEY"))
    search = client.search(query, max_results=10, search_depth="advanced")

    content = [
        {
            'title': s['title'],
            'content': s['content']
        }
        for s in search['results']
    ]

    return content

if __name__ == "__main__":
    mcp.run(transport='stdio')