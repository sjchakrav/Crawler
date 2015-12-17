import sys
import dryscrape
import re
import json
import threading
from flask import Flask, request


app = Flask(__name__)

ds_session = dryscrape.Session()

from bs4 import BeautifulSoup

jobs = {}

next_job_id = 0

def getSoup(link):
    try:
        # html_doc = urllib2.urlopen(link).read()
        ds_session.visit(link)
        return BeautifulSoup(ds_session.body(), 'html.parser')
    except:
        return None

class Crawler:
    linksUsed = []

    def __init__(self, maxLevels, job_id):
        self.maxLevels = maxLevels
        self.job_id = job_id

    def getLinks(self, soup):
        links = []
        for link in soup.find_all('a'):
            if(link.get('href') and re.match('^http',link.get('href'))):
                links.append(link.get('href'))
        return links

    def getImages(self, soup):
        images = []
        for image in soup.find_all('img'):
            if(image.get('src')):
                images.append(re.match('^[^?]+',image.get('src')).group(0))
        return images

    def crawl(self, link, level = 1):
        if(link in self.linksUsed):
            return {}
        self.linksUsed.append(link)
        soup = getSoup(link)
        if(not soup):
            return {}
        links = self.getLinks(soup)
        images = self.getImages(soup)

        print '\t'*(level-1),link

        obj = {}
        obj[link] = images
        if(level < self.maxLevels):
            for link in links:
                for key, arr in self.crawl(link,level+1).iteritems():
                    obj.setdefault(key, [])
                    obj[key] += arr
        return obj

    def crawlAll(self, links):
        global jobs
        print('Initiating Crawl', links, self.job_id)
        obj = {}
        completed = 0
        for link in links:
            for key, arr in self.crawl(link,1).iteritems():
                obj.setdefault(key, [])
                obj[key] += arr
            completed += 1
            jobs[self.job_id]['status']['completed'] = completed
        jobs[self.job_id]['result'] = obj
        return

@app.route("/jobs", methods=['POST'])   # ["http://reddit.com","http://blog.scrapinghub.com"]
def create_job():
    global jobs
    global next_job_id
    try:
        links = json.loads(request.get_data())
        job_id = next_job_id
        # job_id = 0
        next_job_id += 1
        jobs[job_id] = { 'status':{'completed':0, 'inprogress':len(links)} , 'result':None}

        crawler = Crawler(2, job_id)
        t = threading.Thread(target=crawler.crawlAll, args =[links])
        t.daemon = True
        t.start()
        return str(job_id), 202
    except ValueError:
        return 'Bad JSON', 400
    except:
        return 'Error', 500

@app.route('/jobs/<int:job_id>/status', methods=['GET'])
def show_job_status(job_id):
    global jobs
    return json.dumps(jobs[job_id]['status'], sort_keys=True, indent=2)

@app.route('/jobs/<int:job_id>', methods=['GET'])
def show_job_result(job_id):
    global jobs
    return json.dumps({'id':job_id, 'domains':jobs[job_id]['result']}, sort_keys=True, indent=2)

if __name__ == "__main__":
    app.run(debug = False)

# print json.dumps(crawler.crawlAll(sys.argv[1:]), sort_keys=True, indent=4)