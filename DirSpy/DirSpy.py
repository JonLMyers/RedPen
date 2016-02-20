import urllib2
import urllib
import threading
import Queue

threads = 50
target = "http://ctf.arch-cloud.com/"
word_list = "C:\Users\Kierkegaard\Desktop\GitHub\RedPen\DirSpy\search.txt"
resume = None #?
user_agent = "Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11"


def build_worldlist(word_list):

    fb = open(word_list, "rb")
    raw_words = fb.readlines()
    fb.close()

    found_resume = False
    words = Queue.Queue() #?
    for word in raw_words:

        word = word.rstrip() #Strips off right hand spaces.

        if resume is not None:

            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print "Resuming wordlist from: %s" % resume

        else:
            words.put(word)

    return words


def brute_spy(word_queue, extensions = None):

    while not word_queue.empty():

        attempt = word_queue.get()
        attempt_list = []

        if "." not in attempt:
            attempt_list.append("/%s/" % attempt)
        else:
            attempt_list.append("/%s/" % attempt)

        if extensions:
            for extension in extensions:
                attempt_list.append("/%s%s" % (attempt, extension))

        for brute in attempt_list:

            url = "%s%s" % (target, urllib.quote(brute))

            try:
                headers = {}
                headers["User-Agent"] = user_agent
                r = urllib2.Request(url, headers=headers)

                response = urllib2.urlopen(r)

                if len(response.read()):
                    print "[%d] => %s" % (response.code, url)

            except urllib2.URLError, e:

                if hasattr(e, 'code') and e.code != 404:
                    print "!!! %d => %s" % (e.code, url)

                pass

word_queue = build_worldlist(word_list)
extensions = [".php", ".bak", ".orig", ".inc"]

for i in range(threads):
    t = threading.Thread(target=brute_spy, args=(word_queue, extensions,))
    t.start()

