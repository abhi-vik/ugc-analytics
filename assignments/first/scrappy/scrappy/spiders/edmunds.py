# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup

class EdmundsSpider(scrapy.Spider):
    name = 'edmunds'
    allowed_domains = ['edmunds.com']
    start_urls = [f'https://forums.edmunds.com/discussion/2864/general/x/entry-level-luxury-performance-sedans/p{p}' for p in range(1, 723 + 1)]

    def parse(self, response):
        print("procesing:"+response.url)
        usernames = response.css(".Comment .Username::text").getall()
        datetimes = response.css(".Comment .CommentMeta time::attr(datetime)").getall()
        divs = response.css(".Comment .Message.userContent").getall()
        comments = []
        for div in divs:
            soup = BeautifulSoup(div, "html.parser")

            for blockquote in soup('blockquote'):
                blockquote.decompose()

            for br in soup('br'):
                br.decompose()

            text = soup.text.replace('\n', ' ').strip()
            comments.append(text)

        for row in zip(datetimes, usernames, comments):
            scraped_info = {
                'date': row[0],
                'userid': row[1],
                'message': row[2]
            }

            yield scraped_info