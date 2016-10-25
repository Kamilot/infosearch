PAGES = 145151

import re
from simhash import Simhash
import sys

def get_features_ngrams(s):
    width = 3
    s = s.lower()
    s = re.sub(r'[^\w]+', ' ', s)
    words = s.split()
    return [''.join(words[i:i + width]) for i in range(max(len(words) - width + 1, 1))]

with open("hashes.txt", "w", encoding="utf-8") as output:
    for index in range(PAGES):
        with open("docs/{0}.txt".format(index)) as text:
            simh = Simhash(get_features_ngrams(text.read())).value
            output.write("{0}\t{1}\n".format(index, simh))
        if (index % 100 == 0):
            sys.stdout.write("\r{0} documents processed".format(index))
sys.stdout.write("\n")