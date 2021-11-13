
from bs4 import BeautifulSoup
import requests
import re

def getSongText(website: str):

    sWebsiteContent = requests.get(website)
    results = BeautifulSoup(sWebsiteContent.content, "html.parser")

    sSongText = results.find_all('div', id="lyrics")
    sSongText  = str(sSongText).split()

    song = []
    for word in sSongText:
        if (word.startswith("<") == False):
            if (word.find("=") == -1):
                if (word.find("prmtnKeepHeight") == -1): 
                    if (word.find("ADNPM") == -1):
                        if (word.find("]") == -1):
                            if (word.find("[") == -1):
                                song.append(word)
            else:
                if (word.find("lyrics") != -1):
                    song.append(word.replace('id="lyrics>',''))

    song = ' '.join(song)
    song = song.replace('<br/>','').replace('\'',"'")
    return song