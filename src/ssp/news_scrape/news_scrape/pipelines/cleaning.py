'''
Created on 08-Apr-2020

@author: srinivasan
'''
from dateutil import parser 


class DataCorrectionPipeline:
    
    def __init__(self, settings):
        self.settings = settings
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        return pipeline
    
    def process_item(self, item, spider):
        if item and 'published_date' in item and item.get('published_date', None):
            try:
                item['published_date'] = parser.parse(item['published_date'])\
                    .strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                item['published_date'] = ''
        return item
