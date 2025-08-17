import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("TAVILY_API_KEY")
if not API_KEY:
    raise ValueError("TAVILY_API_KEY is not set in environment variables.")

tavily_client = TavilyClient(api_key=API_KEY)

def tavily_search(query: str):
    response = tavily_client.search(query=query)
    return response

def tavily_scrap(urls: list):
    response = tavily_client.extract(urls=urls,format="text")
    return response