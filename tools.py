
# First Step for making our project
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from langchain_core.tools import tool  # Modern LangChain import
from tavily import TavilyClient
from rich import print

# Load environment variables
load_dotenv()

# Initialize Tavily client
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """Search the web for recent and reliable information on a topic. Returns Titles, URLs and snippets."""
    results = tavily.search(query=query, max_results=3)

    out = []
    
    # Safely iterate through results
    for r in results.get('results', []):
        out.append(
            f"Title: {r.get('title')}\n"
            f"URL: {r.get('url')}\n"
            f"Snippet: {r.get('content', '')[:300]}\n"
        )

    return "\n".join(out)

# Because web_search is a LangChain Tool object, you must use .invoke() 
# and pass the arguments as a dictionary.
result = web_search.invoke({"query": "latest AI news"})
print(result)



@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(["script","style", "nav" , "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]     
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

    