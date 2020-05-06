# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.

        
def updateStartURL_processor(request, response):
    request.meta['section'] = response.url.split("/")[-2]
    if 'section' in response.meta:
        request.meta['section'] = response.meta['section']
    return request
