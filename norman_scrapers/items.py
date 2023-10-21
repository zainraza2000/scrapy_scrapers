# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LeaderBoardItem(scrapy.Item):
    stat_origin = scrapy.Field()
    stat_type = scrapy.Field()
    table = scrapy.Field()
    pass
