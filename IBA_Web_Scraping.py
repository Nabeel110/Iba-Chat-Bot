import requests
from bs4 import BeautifulSoup

def get_IBA_news():
    news = ""
    page = get_page()

    if(page==None):
        return "Connection issue"
        

    soup = BeautifulSoup(page.content, 'html.parser')
    base_url = "https://www.iba.edu.pk/"
    for tag in soup.find_all(class_="news-thumb"):
        for txt in tag.stripped_strings:
            news += str(txt)+"\n"

        if("http" in str(tag.a.attrs["href"])):
            news += "Further info: "+ tag.a.attrs["href"]+"\n"

        else:
            news += "Further info: "+ base_url+tag.a.attrs["href"]+"\n"

    news = news.strip()
    return news



def get_page():
    url = 'https://www.iba.edu.pk/'
    page = None

    retries = -1
    while(page == None):
        retries += 1
        try:
            page = requests.get(url, timeout=10)

        except Exception:
            pass

        if(retries > 4):
            return page

    #print(retries)
    return page

