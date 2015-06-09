import scrapy

class UserItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    comment = scrapy.Field()
