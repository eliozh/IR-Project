import re
import scrapy
import string
import random

from ..validator import match_year, process_slash_str
from ..items import MovieItem
from ..database import col


class MovieSpider(scrapy.Spider):
    name = 'movie_spider'
    allowed_domains = ['movie.douban.com']

    r = col.find(projection={'_id': False, 'link': True})
    crawled = list(map(lambda i: i['link'], r))
    if not crawled:
        start_urls = ['https://movie.douban.com/subject/1292052']
    else:
        start_urls = crawled

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    @staticmethod
    def get_douban_id(item, response):
        regx = r'https://movie.douban.com/subject/(\d+).*'
        item['douban_id'] = re.match(regx, response.url).group(1)
        return item

    @staticmethod
    def get_types(item, response):
        regx = '//text()[preceding-sibling::span[text()="集数:"]][following-sibling::br]'
        data = response.xpath(regx).extract()

        if data:
            item['types'] = 'tv'
        else:
            item['types'] = 'movie'
        return item

    @staticmethod
    def get_cover(item, response):
        regx = '//img[@rel="v:image"]/@src'
        data = response.xpath(regx).extract()
        if data:
            item['cover'] = data[0].replace('s_ratio_poster', 'l_ratio_poster')
        else:
            item['cover'] = ''
        return item

    @staticmethod
    def get_link(item, response):
        regx = r'https://movie.douban.com/subject/(\d+)'
        item['link'] = re.match(regx, response.url).group(0)
        return item

    @staticmethod
    def get_name(item, response):
        regx = '//title/text()'
        data = response.xpath(regx).extract()
        if data:
            item['name'] = data[0][:-5].strip()
        return item

    @staticmethod
    def get_year(item, response):
        regx = '//span[@class="year"]/text()'
        data = response.xpath(regx).extract()
        if data:
            item['year'] = match_year(data[0])
        return item

    @staticmethod
    def get_directors(item, response):
        regx = '//a[@rel="v:directedBy"]/text()'
        directors = response.xpath(regx).extract()
        item['directors'] = directors
        return item
    
    @staticmethod
    def get_actors(item, response):
        regx = '//a[@rel="v:starring"]/text()'
        actors = response.xpath(regx).extract()
        item['actors'] = actors
        return item
    
    @staticmethod
    def get_score(item, response):
        regx = '//strong[@property="v:average"]/text()'
        data = response.xpath(regx).extract()
        if data:
            item['score'] = data[0]
        return item
    
    @staticmethod
    def get_votes(item, response):
        regx = '//span[@property="v:votes"]/text()'
        data = response.xpath(regx).extract()
        if data:
            item['votes'] = data[0]
        return item

    @staticmethod
    def get_summary(item, response):
        regx = '//span[@property="v:summary"]/text()'
        data = response.xpath(regx).extract()
        if data:
            item['summary'] = data[0].strip()
        else:
            item['summary'] = ''
        return item
    
    def parse(self, response):
        if response.status == 302:
            return
        else:
            item = MovieItem()
            self.get_douban_id(item, response)
            self.get_types(item, response)
            self.get_cover(item, response)
            self.get_link(item, response)
            self.get_name(item, response)
            self.get_year(item, response)
            self.get_directors(item, response)
            self.get_actors(item, response)
            self.get_score(item, response)
            self.get_votes(item, response)
            self.get_summary(item, response)
            self.crawled.append(item['link'])
            yield item

        next_page = response.xpath('//dl/dd/a/@href').extract()
        if next_page is not None:
            for page in next_page:
                if page not in self.crawled:
                    yield scrapy.Request(page, callback=self.parse)
            return
