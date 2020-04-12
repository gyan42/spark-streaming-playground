# -*- coding: utf-8 -*-
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders.crawl import Rule, CrawlSpider
from w3lib.html import remove_tags, replace_escape_chars

from news_scrape.items import NewsScrapeItem


class ThehinduSpider(CrawlSpider):
    name = 'thehindu'
    allowed_domains = ['thehindu.com']
    start_urls = ['https://www.thehindu.com/news/national/',
                  'https://www.thehindu.com/news/international/',
                  'https://www.thehindu.com/business/',
                  'https://www.thehindu.com/sport/']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5
        }
    
    rules = (Rule(LxmlLinkExtractor(restrict_xpaths=('//*[@class="search-scrollar"][2]/ul[@class="pagination"]/li[@class="next page-item"]/a',))
               , follow=True,),
          Rule (LxmlLinkExtractor(restrict_css=('div.Other-StoryCard h3 a.Other-StoryCard-heading'))
                , callback='parse_article',),
          )
    
    def parse_article(self, response): 
        il = ItemLoader(item=NewsScrapeItem(), response=response)
        il.default_input_processor = MapCompose(lambda v: v.strip(),
                                                remove_tags, replace_escape_chars)
        il.add_css('headline', 'div.article div h1.title::text')
        il.add_css('synopsis', 'div.article div h2.intro::text')
        il.add_css('tags', 'div.morein-tag-cont div.tag-button a::text')
        il.add_css('authors', 'div.article div div.author-container.hidden-xs span.author-img-name a.auth-nm::text')
        il.add_css('published_date', 'div.article div div.author-container.hidden-xs div.ut-container span.blue-color.ksl-time-stamp none::text')
        il.add_css('place', 'div.article div div.author-container.hidden-xs div.ut-container span.blue-color.ksl-time-stamp:first-child::text',
                   MapCompose(lambda v: v.replace(',', '')))
        il.add_value('link', response.url)
        il.add_xpath('content', '//div[contains(@id,"content-body")]//p//text()')
        il.add_value('domain', 'thehindu.com')
        il.add_css('section', 'div.article div div.article-exclusive a.section-name::text')
        yield il.load_item()
