'''
Created on 06-Apr-2020

@author: srinivasan
'''
import logging
from scrapy.utils.serialize import ScrapyJSONEncoder

logger = logging.getLogger(__name__)


class KafkaPipeline:
    
    stats_name = 'KafkaPipeline'
    
    def __init__(self, settings, stats):
        from pykafka.client import KafkaClient
        self.stats = stats
        self.settings = settings
        self.encoder = ScrapyJSONEncoder()
        self.client = KafkaClient(hosts=settings.get('KAFKA_BOOTSTRAP_SERVERS'))
        self.producer = self.client.topics[bytes(settings.get('KAFKA_TOPIC_NAME'), 'ascii')]\
        .get_sync_producer(min_queued_messages=1)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings, crawler.stats)
    
    def process_item(self, item, spider):
        itemval = item if isinstance(item, dict) else dict(item)
        itemval['spider'] = spider.name
        self.producer.produce(bytes(self.encoder.encode(itemval),
                                            'ascii'))
        self.stats.inc_value('{}/produce'.format(self.stats_name), spider=spider)
        logger.info("Item sent to Kafka")
        return itemval
    
    def close_spider(self, spider):
        if self.producer:
            self.producer.stop()
