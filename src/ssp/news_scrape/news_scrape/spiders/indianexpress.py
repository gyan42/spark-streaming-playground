# -*- coding: utf-8 -*-
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders.crawl import Rule, CrawlSpider
from w3lib.html import remove_tags, replace_escape_chars

from news_scrape.items import NewsScrapeItem
from news_scrape.spiders import updateStartURL_processor


class IndianexpressSpider(CrawlSpider):
    name = 'indianexpress'
    allowed_domains = ['indianexpress.com']
    start_urls = ['https://indianexpress.com/section/india/', 'https://indianexpress.com/section/world/',
                  'https://indianexpress.com/section/cities/', 'https://indianexpress.com/section/sports/',
                  'https://indianexpress.com/section/lifestyle/', 'https://indianexpress.com/section/opinion/',
                  'https://indianexpress.com/section/entertainment/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5
        }
    
    rules = (Rule(LxmlLinkExtractor(restrict_xpaths=('//a[@class="next page-numbers"]',))
               , follow=True,
               process_request=updateStartURL_processor),
          Rule (LxmlLinkExtractor(restrict_css=('div.nation > div.articles > h2 > a',
                                                'div.profile-container > div.opi-story > h2 > a',
                                                'div.nation > div.articles > div.title > a'))
                , callback='parse_article',
                 process_request=updateStartURL_processor),
          )

    def parse_article(self, response):
        il = ItemLoader(item=NewsScrapeItem(), response=response)
        il.default_input_processor = MapCompose(lambda v: v.strip(),
                                                remove_tags, replace_escape_chars)
        il.add_css('headline', 'h1.native_story_title::text')
        il.add_css('synopsis', 'h2.synopsis::text')
        il.add_css('content', 'div.articles div.full-details p::text',
                  lambda x: x[:len(x) - 2])
        il.add_xpath('tags', '//div[@class="storytags"]//li/a//text()')
        il.add_xpath('authors', '//div[@id="storycenterbyline"]/a//text()')
        il.add_xpath('published_date', '//div[@id="storycenterbyline"]/span//text()',
                     MapCompose(lambda x:x.split(':', 1)[1] if len(x.split(':', 1)) > 1 else x)
                     )
        il.add_xpath('place', '//div[@id="storycenterbyline"]/text()',
                     MapCompose(lambda x:x.replace("|", '')  if '|' in x else None))
        il.add_value('link', response.url)
        il.add_value('domain', 'indianexpress.com')
        il.add_value('section', response.meta.get('section', ''))
        yield il.load_item()
        
