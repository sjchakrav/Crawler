import sys
import urllib2
import re
import json

from bs4 import BeautifulSoup

def getSoup(link):
    try:
        html_doc = urllib2.urlopen(link).read()
    except:
        return None
    else:
        return BeautifulSoup(html_doc, 'html.parser')

class Crawler:
    linksUsed = []

    def __init__(self, maxLevels):
        self.maxLevels = maxLevels

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

        print '\t',link, level

        obj = {}
        obj[link] = images
        if(level < self.maxLevels):
            for link in links:
                for key, arr in self.crawl(link,level+1).iteritems():
                    obj.setdefault(key, [])
                    obj[key] += arr
        return obj

    def crawlAll(self, links, level = 1):
        obj = {}
        for link in links:
            for key, arr in self.crawl(link,level).iteritems():
                obj.setdefault(key, [])
                obj[key] += arr
        return obj

crawler = Crawler(2)

print json.dumps(crawler.crawlAll(sys.argv[1:]), sort_keys=True, indent=4)
