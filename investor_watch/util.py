import requests 
from bs4 import BeautifulSoup


headers = {
    'User-Agent': 'Mozilla/5.0'
}
def web_scrape_content(article_url) -> list[str]:
    '''
    Scrapes an articles content on yahoo finance.
    '''

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    response = requests.get(article_url, headers=headers)
    html = response.text

    # Parse it with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    # Find all <p> tags with the class `yf-1090901`
    paragraphs = soup.find_all("p", class_="yf-1090901")

    content = []
    # Extract and print the cleaned text
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 100: content.append(text)                 # get only the long paragraphs 
    
    return content

    

def web_scrape_tags(article_url) -> list[str]: 
    '''Finds the related stocks that the article tags'''

    response = requests.get(article_url, headers=headers)
    html = response.text

    # Parse it with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    spans = soup.find_all("span", class_="symbol yf-5ogvqh")

    # Extract and print the cleaned text
    return [s.get_text(strip=True) for s in spans]

    

# print(web_scrape_content('https://finance.yahoo.com/news/third-point-details-stakes-u-001227888.html'))
