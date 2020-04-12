# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, Join


class NewsScrapeItem(scrapy.Item):
    # define the fields for your item here like:
    headline = scrapy.Field(output_processor=TakeFirst())
    synopsis = scrapy.Field(output_processor=TakeFirst())
    link = scrapy.Field(output_processor=TakeFirst())
    authors = scrapy.Field()
    published_date = scrapy.Field(output_processor=TakeFirst())
    place = scrapy.Field(output_processor=TakeFirst())
    domain = scrapy.Field(output_processor=TakeFirst())
    section = scrapy.Field(output_processor=TakeFirst())
    content = scrapy.Field(output_processor=Join())
    tags = scrapy.Field()
