import scrapy

from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup

def parse_rating(rating):
    rating_list = list(map(lambda v: v.strip().split(':'), rating.split('|')))
    return { k:float(v.strip()) for k, v in rating_list }

def parse_block(div):
    soup = BeautifulSoup(div, "html.parser")

    for span in soup('span'):
        span.decompose()
        
    for br in soup('br'):
        br.decompose()

    return soup.text.replace('\n', ' ').strip()[5:]

class BeerSpider(scrapy.Spider):
    name = 'beer'
    allowed_domains = ['beeradvocate.com']
    base_url = 'https://www.beeradvocate.com'
    start_urls = [base_url + '/beer/top-rated']
    custom_settings = {
        'LOG_LEVEL': 'INFO',
        'FEED_URI' : 'output.csv',
        'FEED_FORMAT': 'csv'
    }
    
    def parse(self, response):
        beer_urls = response.css('#ba-content>table tr>.hr_bottom_light:nth-child(2n)>a::attr(href)').getall()
        
        for beer_url in beer_urls:
            yield scrapy.Request(self.base_url + beer_url, callback=self.parse_child)
            
    def parse_child(self, response):
        name = response.css('.titleBar h1::text').get()
        ratings = response.css('#rating_fullview_content_2 span:nth-child(5)::text').getall()
        comments = [parse_block(div) for div in response.css('#rating_fullview_content_2').getall()]

        for row in zip(ratings, comments):
            yield {
                'beer': name,
                **parse_rating(row[0]),
                'comment': row[1]
            }
        
        next_url = response.xpath("//a[contains(text(), 'next')]/@href").get()
        if next_url is not None:
            yield scrapy.Request(self.base_url + next_url, callback=self.parse_child)

process = CrawlerProcess()
process.crawl(BeerSpider)
process.start()