from bs4 import BeautifulSoup

def get_text(page):
    soup = BeautifulSoup(page, "lxml")
    result = ""
    tag = soup.find_all("h1", id="firstHeading")[0]
    result += tag.get_text() + "\n"
    tag = soup.find_all("div", id="mw-content-text")[0]
    for div in tag.find_all("div"):
        div.extract()
    for table in tag.find_all("table"):
        table.extract()
    for span in tag.find_all("span", class_="mw-editsection"):
        span.extract()
    result += tag.get_text()
    return result
    
urlsfile = open("urls_pp.txt")

urls = []
for line in urlsfile:
    index, url = line.split()
    index = int(index)
    urls.append(url)
    
for index in range(start, len(urls)):
    with open("docs/{0}.html".format(index), encoding="utf-8") as f:
        page = f.read()
    text = get_text(page)
    with open("docs/{0}.txt".format(index), "w", encoding="utf-8") as f:
        f.write(text)
    if index % 100 == 0:
        print(index)