from urllib.request import urlopen
from html.parser import HTMLParser
from urllib.parse import urljoin
from urllib.error import HTTPError
import queue
from threading import Thread, Lock

logs = open("logs.txt", "w")

def update_url(url):
    try:
        with urlopen(url) as response:
            url = response.geturl()
        return url
    except HTTPError as e:
        print("Error", url, e.code, file=logs)
        print("Error", url, e.code)
        return None

class HTMLPage:
    def __init__(self, url):
        self.edges_out = set()
        self.edges_in = set()
        self.url = url
        self.lock = Lock()

    def get(self):
        with urlopen(self.url) as response:
            page = str(response.read(), encoding="utf-8")
        return page

class WebGraph:
    def __init__(self):
        self.pages = []
        self.url_to_id = dict()
        self.lock = Lock()

    def get_id(self, url, callback=None):
        if url in self.url_to_id:
            return self.url_to_id[url]
        url = update_url(url)
        if url is None:
            return None
        self.lock.acquire()
        if url not in self.url_to_id:
            index = len(self.pages)
            self.pages.append(HTMLPage(url))
            self.url_to_id[url] = index
            self.lock.release()
            if callback is not None:
                callback(index)
            return index
        self.lock.release()
        return self.url_to_id[url]

    def add_links(self, origin, links, callback=None):
        for link in links:
            destination = self.get_id(link, callback)
            if destination is not None:
                with self.pages[origin].lock:
                    self.pages[origin].edges_out.add(destination)
                with self.pages[destination].lock:
                    self.pages[destination].edges_in.add(origin)

    def write_urls(self, filename="urls.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, self.pages[i].url))

    def write_graph(self, filename="graph.txt"):
        with open(filename, "w", encoding="utf-8") as f:
            for i in range(len(self.pages)):
                f.write("{0}\t{1}\n".format(i, " ".join(str(x) for x in self.pages[i].edges_out)))



class WikiParser(HTMLParser):
    FORBIDDEN = ("Special:",
                 "Wikipedia:",
                 "User:",
                 "User_talk:",
                 "File:",
                 "Wikipedia_talk:",
                 "Template:",
                 "Template_talk:",
                 "Talk:",
                 "Help_talk:",
                 "T:"
                 )
    HEADER = "https://simple.wikipedia.org/wiki/"

    def __init__(self, base, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base = base
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    candidate = str(urljoin(self.base, value))
                    last_slash = candidate.rfind("/")
                    last_jail = candidate.rfind("#")
                    if (last_jail > last_slash):
                        candidate = candidate[:last_jail]
                    if not candidate.startswith(self.HEADER):
                        return
                    for word in self.FORBIDDEN:
                        if candidate.startswith(word, len(self.HEADER)):
                            return
                    self.links.append(candidate)


unparsed_pages = queue.Queue()
graph = WebGraph()
working_threads = 0
working_lock = Lock()
running = True

def queue_adder(id):
    unparsed_pages.put(id)

def parse_page(id):
    page = graph.pages[id].get()
    parser = WikiParser(graph.pages[id].url)
    parser.feed(page)
    graph.add_links(id, parser.links, queue_adder)
    with open("pages/{0}.html".format(id), "w", encoding="utf-8") as f:
        f.write(page)

def worker(id):
    global working_threads
    global running
    first = True
    while running:
        try:
            index = unparsed_pages.get(True, 0.5)
            if first:
                with working_lock:
                    working_threads += 1
                    first = False
            try:
                parse_page(index)
                print(id, ": Page", index, "parsed. Total: ", len(graph.pages))
                print(id, ":", graph.pages[index].url, "written to", index, file=logs)
            except Exception as e:
                print(id, ": Error", index, e, file=logs)
                print(id, ": Error", index, e)
                unparsed_pages.put(index)
        except queue.Empty:
            with working_lock:
                if working_threads == 0:
                    print(id, ": Thread finished")
                    return
                else:
                    if not first:
                        working_threads -= 1
                        first = True
    if not first:
        with working_lock:
            working_threads -= 1
    print(id, ": Thread finished")

THREADS = 16

try:
    graph.get_id("https://simple.wikipedia.org/wiki/Main_Page", queue_adder)
    threads = [Thread(target=worker, args=(i,)) for i in range(THREADS)]
    for thread in threads:
        thread.start()
    finish = False
    while not finish:
        finish = True
        for thread in threads:
            if thread.is_alive():
                thread.join(1.0)
                if thread.is_alive():
                    finish = False

except KeyboardInterrupt:
    print("hello interrupt")
    running = False
    for i in range(THREADS):
        if threads[i].is_alive():
            threads[i].join(20.0)
            if threads[i].is_alive():
                print("Thread {0} failed to finish".format(i))
                print("Thread {0} failed to finish".format(i), file=logs)
finally:
    logs.close()
    graph.write_urls()
    graph.write_graph()

