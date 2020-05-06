# -*- coding: utf-8 -*-
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.spiders.crawl import Rule, CrawlSpider
from w3lib.html import remove_tags, replace_escape_chars

from news_scrape.items import NewsScrapeItem
from news_scrape.spiders import updateStartURL_processor


class NewindianexpressSpider(CrawlSpider):
    name = 'newindianexpress'
    allowed_domains = ['newindianexpress.com']
    start_urls = ['https://www.newindianexpress.com/nation',
                  'https://www.newindianexpress.com/world',
                  'https://www.newindianexpress.com/business',
                  'https://www.newindianexpress.com/good-news']
    
    custom_settings = {
        'DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 5
        }
    
    rules = (Rule(LxmlLinkExtractor(restrict_xpaths=('//div[@class="pagina"]/a[contains(text(),">")]',))
               , follow=True,
               process_request=updateStartURL_processor),
          Rule (LxmlLinkExtractor(restrict_css=('a.article_click'))
                , callback='parse_article',
                 process_request=updateStartURL_processor),
          )
    
    def parse_article(self, response): 
        il = ItemLoader(item=NewsScrapeItem(), response=response)
        il.default_input_processor = MapCompose(lambda v: v.strip(),
                                                remove_tags, replace_escape_chars)
        il.add_css('headline', 'h1#content_head.ArticleHead::text')
        il.add_css('synopsis', 'div.straptxt.article_summary p::text')
        il.add_css('content', 'div#storyContent.articlestorycontent p::text')
        il.add_css('tags', '.tags > a::text')
        il.add_css('authors', 'div.agency_txt span.author_des span::text')
        il.add_css('published_date', '.ArticlePublish > span:nth-child(1)::text')
        il.add_css('place', '#storyContent > p:nth-child(2)::text',
                   MapCompose(lambda x:x.split(':', 1)[0] if len(x.split(':', 1)) > 1 else None))
        il.add_value('link', response.url)
        il.add_value('domain', 'newindianexpress.com')
        il.add_value('section', response.meta.get('section', ''))
        yield il.load_item()
