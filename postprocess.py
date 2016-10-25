from shutil import copyfile
import os

urlsfile = open("urls.txt")
graphfile = open("graph.txt")

FORBIDDEN = ("Main_Page/",
             "Special:",
             "Special_talk:",
             "Wikipedia:",
             "Wikipedia_talk:",
             "User:",
             "User_talk:",
             "File:",
             "File_talk:",
             "Image:",
             "Image_talk",
             "Template:",
             "Template_talk:",
             "Talk:",
             "Help_talk:",
             "Category:",
             "Category_talk:",
             "Module:",
             "MediaWiki:",
             "MediaWiki_talk:",
             "Portal:",
             "Portal_talk:",
             "T:"
             )

PREFIX = "https://simple.wikipedia.org/wiki/"

def fit(url):
    if not url.startswith(PREFIX):
        return False
    for word in FORBIDDEN:
        if url.startswith(word, len(PREFIX)):
            return False
    return True

class HTMLPage:
    def __init__(self, url, old_id):
        self.edges_out = set()
        self.edges_in = set()
        self.old_id = old_id
        self.url = url

class WebGraph:
    def __init__(self):
        self.pages = []

    def add_page(self, url, index, edges):
        self.pages.append(HTMLPage(url, index))
        self.pages[-1].edges_out = set(edges)

    def recalculate_edges(self, ids):
        for i, page in enumerate(self.pages):
            page.edges_out = set(ids[edge] for edge in page.edges_out if ids[edge] != -1)
            for edge in page.edges_out:
                self.pages[edge].edges_in.add(i)

    def copy_pages(self, first_dir="pages", second_dir="docs"):
        if os.path.exists(second_dir) and not os.path.isdir(second_dir):
            return
        if not os.path.exists(second_dir):
            os.mkdir(second_dir)
        for i, page in enumerate(self.pages):
            src = "{0}/{1}.html".format(first_dir, page.old_id)
            dest = "{0}/{1}.html".format(second_dir, i)
            copyfile(src, dest)

    def write_urls(self, filename="urls_pp.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, self.pages[i].url))

    def write_graph(self, filename="graph_pp.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, " ".join(str(x) for x in self.pages[i].edges_out)))

ids = []
graph = WebGraph()

for line in urlsfile:
    edges = [int(x) for x in graphfile.readline().rstrip().split()[1:]]
    index, url = line.split()
    index = int(index)
    if not fit(url):
        ids.append(-1)
    else:
        graph.add_page(url, index, edges)
        ids.append(len(graph.pages) - 1)
    if index % 100 == 0:
        print(index, "pages done")

graph.recalculate_edges(ids)
graph.write_urls()
graph.write_graph()
#graph.copy_pages()
