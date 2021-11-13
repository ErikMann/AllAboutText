
from bs4 import BeautifulSoup
import requests

def scraperSongtexts(website: str):

    sWebsiteContent = requests.get(website)
    soup = BeautifulSoup(sWebsiteContent.content, 'html.parser')
    links_with_text = []
    for a in soup.find_all('a', href=True): 
        if a.text: 
            links_with_text.append(a['href'])

    links =[link for link in links_with_text if "/songtext/" in link]

    websits = []
    for link in links:
        link = link.replace('../../', '')
        websits.append('https://www.songtexte.com/' + link)
    return websits


