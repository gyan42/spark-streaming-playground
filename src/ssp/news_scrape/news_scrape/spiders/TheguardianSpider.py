# -*- coding: utf-8 -*-
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders.crawl import Rule, CrawlSpider
from w3lib.html import remove_tags, replace_escape_chars

from news_scrape.items import NewsScrapeItem


class TheguardianspiderSpider(CrawlSpider):
    name = 'theguardianSpider'
    allowed_domains = ['theguardian.com']
    start_urls = ['https://www.theguardian.com/world/all']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5
        }
    
    rules = (Rule(LxmlLinkExtractor(restrict_xpaths=(
        '//*[contains(@class,"pagination__action--static") and contains(@rel,"next")]',))
               , follow=True,),
          Rule (LxmlLinkExtractor(restrict_xpaths=('//*[contains(@class,"fc-item__link")]'))
                , callback='parse_article',),
          )
    
    def parse_article(self, response):    
        il = ItemLoader(item=NewsScrapeItem(), response=response)
        il.default_input_processor = MapCompose(lambda v: v.strip(),
                                                remove_tags, replace_escape_chars)
        il.add_xpath('headline', '//*[contains(@itemprop,"headline")]//text()')
        il.add_xpath('synopsis', '//*[contains(@class,"content__article-body")]//p//text()')
        #il.add_css('synopsis', '//*[contains(@class,"content__article-body")]//p//text()')
        il.add_xpath('tags', '//*[contains(@class,"label__link-wrapper")]//text()')
        il.add_xpath('authors', '//*[contains(@rel,"author")]//*/text()')
        il.add_xpath('published_date', '//*[contains(@class,"content__dateline-wpd")]//@datetime')
        il.add_value('place', '')
        il.add_value('link', response.url)
        il.add_value('domain', 'theguardian.com')
        il.add_value('section', '')        
        yield il.load_item()
