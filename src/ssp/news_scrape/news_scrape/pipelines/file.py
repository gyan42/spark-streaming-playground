'''
Created on 06-Apr-2020

@author: srinivasan
'''
import os
from scrapy import signals
from scrapy.exporters import JsonLinesItemExporter


class MixinCreateFolder:
    
    def createFolder(self, outpath):
        from pathlib import Path
        p = Path(outpath).parent
        if not p.exists():
            p.mkdir(parents=True)


class JsonFileWriter(MixinCreateFolder):
    
    def __init__(self, settings):
        self._settings = settings

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(crawler.settings)
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        
        outpath = os.path.join(self._settings.get('STORAGE_DIR'),
                               '%s_items.json' % spider.name)
        self.createFolder(outpath)
        self.file = open(outpath, 'w+b')
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
