# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MovieItem(scrapy.Item):
    # define the fields for your item here like:
    douban_id = scrapy.Field()
    types = scrapy.Field()
    cover = scrapy.Field()
    link = scrapy.Field()
    name = scrapy.Field()
    year = scrapy.Field()
    directors = scrapy.Field()
    actors = scrapy.Field()
    score = scrapy.Field()
    votes = scrapy.Field()
    summary = scrapy.Field()
