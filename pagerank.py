import sys
from collections import deque

class HTMLPage:
    def __init__(self, url):
        self.edges_out = set()
        self.edges_in = set()
        self.url = url
        self.dist = -1
        self.pagerank = 0

class WebGraph:
    def __init__(self):
        self.pages = []

    def read(self, urlsfilename="urls_pp.txt", graphfilename="graph_pp.txt"):
        with open(urlsfilename) as urlsfile:
            with open(graphfilename) as graphfile:
                for line in urlsfile:
                    edges = [int(x) for x in graphfile.readline().rstrip().split()[1:]]
                    index, url = line.split()
                    index = int(index)
                    self.add_page(url, edges)
                    if index % 100 == 0:
                        sys.stdout.write("\r{0} pages read".format(index))
        sys.stdout.write("\n")

    def read_ranks(self, ranksfilename="ranks.txt"):
        with open(ranksfilename) as ranksfile:
            for line in ranksfile:
                index, rank = line.split('\t', 1)
                index = int(index)
                rank = float(rank)
                self.pages[index].pagerank = rank

    def add_page(self, url, edges):
        self.pages.append(HTMLPage(url))
        self.pages[-1].edges_out = set(edges)
        
    def count_in_edges(self):
        for index, page in enumerate(self.pages):
            for edge in page.edges_out:
                self.pages[edge].edges_in.add(index)
                
    def calculate_distances(self):
        q = deque([0])
        self.pages[0].dist = 0
        while len(q) != 0:
            vertex = q.popleft()
            for edge in self.pages[vertex].edges_out:
                if self.pages[edge].dist == -1:
                    self.pages[edge].dist = self.pages[vertex].dist + 1
                    q.append(edge)

    def write_urls(self, filename="urls_pp.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, self.pages[i].url))

    def write_graph(self, filename="graph_pp.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, " ".join(str(x) for x in self.pages[i].edges_out)))

    def write_ranks(self, filename="ranks.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, self.pages[i].pagerank))

graph = WebGraph()
graph.read()

damping = 0.85
iterations = 200

for page in graph.pages:
    page.prev_value = 1 / len(graph.pages)

for iteration in range(iterations):
    for page in graph.pages:
        page.pagerank = (1 - damping) / len(graph.pages)
    for page in graph.pages:
        for edge in page.edges_out:
            graph.pages[edge].pagerank += damping * page.prev_value / len(page.edges_out)
    for page in graph.pages:
        page.prev_value = page.pagerank
    sys.stdout.write("\r{0} iterations done".format(iteration))

sys.stdout.write("\n")

graph.write_ranks()