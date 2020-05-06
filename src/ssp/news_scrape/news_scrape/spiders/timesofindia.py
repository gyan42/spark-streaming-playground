# -*- coding: utf-8 -*-
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders.crawl import Rule, CrawlSpider
from w3lib.html import remove_tags, replace_escape_chars

from news_scrape.items import NewsScrapeItem


class TimesofindiaSpider(CrawlSpider):
    name = 'timesofindia'
    allowed_domains = ['timesofindia.indiatimes.com']
    start_urls = ['https://timesofindia.indiatimes.com/india']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5
        }
    
    rules = (Rule(LxmlLinkExtractor(restrict_xpaths=('//div[@id="c_wdt_list_1"]//ul[@class="curpgcss"]/li[@class=".current"]/following-sibling::li[1]/a',))
               , follow=True,),
          Rule (LxmlLinkExtractor(restrict_css=('div#c_wdt_list_1 ul.list5.clearfix li span.w_tle a'))
                , callback='parse_article',),
          )
    
    def parse_article(self, response): 
        il = ItemLoader(item=NewsScrapeItem(), response=response)
        il.default_input_processor = MapCompose(lambda v: v.strip(),
                                                remove_tags, replace_escape_chars)
        il.add_css('headline', 'div._38kVl h1.K55Ut::text')
        il.add_value('synopsis', '')
        il.add_css('content', 'div._1IaAp.clearfix div._3WlLe.clearfix::text')
        il.add_value('tags', '')
        il.add_css('authors', 'div._38kVl div._3JRp7 div._3Mkg-.byline::text',
                  MapCompose(lambda x:x.split('|')[0] if len(x.split('|')) > 1 else ''))
        il.add_css('published_date', 'div._38kVl div._3JRp7 div._3Mkg-.byline::text',
                   MapCompose(lambda x:x.split('|')[-1] if len(x.split('|')) > 1 else '',
                              lambda y:y.replace('Updated:', '')))
        
        il.add_css('place', 'div._1IaAp.clearfix div._3WlLe.clearfix::text',
                      MapCompose(lambda x:x.split(':', 1)[0] if len(x.split(':', 1)) > 1 else x))
        il.add_value('link', response.url)
        il.add_value('domain', 'timesofindia.indiatimes.com')
        il.add_value('section', '')
        yield il.load_item()
