urlsfile = open("urls_pp.txt")

urls = []
for line in urlsfile:
    index, url = line.split()
    index = int(index)
    urls.append(url)
    
