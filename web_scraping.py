import requests
from bs4 import BeautifulSoup 

def get_web_lyrics(input_text):
    
    search_name = input_text.replace(' ', '%20')
    # search_name = "just%20carry%20on"
    URL = "https://mojim.com/{}.html?t3".format(search_name)
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    dd = soup.find("dd", class_="mxsh_dd1")

    span = dd.find("span", class_="mxsh_ss4")

    a = span.find("a", href=True)

    page = requests.get("https://mojim.com{}".format(a['href']))

    soup2 = BeautifulSoup(page.content, "html.parser")

    dd2 = soup2.find("dd", class_="fsZx3")

    for dummy in dd2.find_all(['br', 'a', 'ol']):
        dummy.extract()

    output_text = str(dd2.prettify())
    start = output_text.index('>') + 1
    end = len(output_text) - 5
    output_text = output_text[start:end:]
    output_text = output_text.replace('更多更詳盡歌詞 在\n ', '')

    # print(output_text)
    return output_text

    # print(dd2.prettify())
    # with open('web.txt', 'w', encoding="utf-8") as f:
    #     f.write(page.text)

    # with open('a.txt', 'w', encoding="utf-8") as f:
    #     f.write(output_text)