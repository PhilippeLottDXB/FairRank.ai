import requests
from bs4 import BeautifulSoup

def bing_search(query, num_results=10):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    search_url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for result in soup.select("li.b_algo h2 a")[:num_results]:
        href = result.get("href")
        if href:
            links.append(href)

    return links

def scrape_page_content(url):
    headers = {
        "User-Agent": "Chrome/5.0"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(response)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        print(soup)

        # Extract visible text from the page
        paragraphs = soup.find_all("p")
        content = "\n".join(p.get_text() for p in paragraphs if p.get_text().strip())

        return content[:]  # Return first 1000 characters for brevity
    except Exception as e:
        return f"Failed to scrape {url}: {e}"


# Example usage
query = "Philippe Lott, PhD engineer, CFD, Turbmachinery"
results = bing_search(query)

for i, link in enumerate(results, 1):
    print(f"{i}. {link}")
    print(scrape_page_content(link))

urls = [
    "https://realpython.com/python-web-scraping-practical-introduction/",
    "https://www.geeksforgeeks.org/python-web-scraping-tutorial/"
]

for url in urls:
    print(f"\n--- Content from: {url} ---")
    print(scrape_page_content(url))
    