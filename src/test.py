import requests
from bs4 import BeautifulSoup

url = "https://en.wikipedia.org/wiki/ISO_3166-2:RU"

res = requests.get(url)
soup = BeautifulSoup(res.text, "html.parser")
print("{")
for items in soup.find_all("span", {"class": "monospaced"}):
    print('"' + items.text + '" :' + ' "",')
    # print(data)
print("}")
