import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from db_data import get_onderneming_2, insert_query
from urllib.parse import urlparse
from threading import Lock

from scrapy.exceptions import IgnoreRequest, NotConfigured
import re
def formaturl(url):
    if not re.match('(?:http|ftp|https)://', url):
        return 'https://{}'.format(url)
    
class WebSpider(scrapy.Spider):
    
    name = "webspider"
   
    DEPTH_LIMIT = 3
    
   
     

    def __init__(self):
        self.links=[]
        self.allowed_domains = []
        for row in get_onderneming_2():
            self.allowed_domains.append(row[4].replace("https://www.", "").replace("www.", "").replace("/", ""))


    def start_requests(self):
        for row in get_onderneming_2():
            
            yield scrapy.Request(formaturl(row[4]) ,
                         callback = self.parse , cb_kwargs={'comp':row[1], 'count' : 0})

    
        
    # include_patterns = ['']
    exclude_patterns = ['.*\.(css|js|gif|jpg|jpeg|png|Store|Contact)']

   


    response_type_whitelist = ['text/html']
    


    def parse(self, response, comp, count):
        if count <= 3 :
            str1 = ""
            print("///////////////////////")
            print( response.url  )
            print(comp)
            text = ''.join(response.selector.xpath("//body//text()").extract() )
            print("///////////////////////")
            query = 'INSERT INTO dep."html_paginas"("naam","url", "text") VALUES(  %s,%s,%s ) '
            insert_query(query, comp, response.url, text)
            for url in LinkExtractor(allow_domains=self.allowed_domains).extract_links(response):
                if url:
                    print(url)
                    yield    response.follow(url = url,
                                callback = self.parse,cb_kwargs={'comp':comp, 'count' : count+1})
        
        else: 
            print(f"{count} DONE ON DEPTH")

   
    
process = CrawlerProcess()

process.crawl(WebSpider)
process.start()
