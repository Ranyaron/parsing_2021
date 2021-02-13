# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class GbParsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class AutoyoulaItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    description = scrapy.Field()
    author = scrapy.Field()
    specifications = scrapy.Field()
    price = scrapy.Field()


class HhruAdsItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    url_author = scrapy.Field()


class HhruAuthorItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    areas = scrapy.Field()
    description = scrapy.Field()
    vacancies = scrapy.Field()


class HhruAuthorAdsItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    description = scrapy.Field()
    skills = scrapy.Field()
    url_author = scrapy.Field()


class InstagramItem(scrapy.Item):
    _id = scrapy.Field()
    data = scrapy.Field()
    date = scrapy.Field()


class InstagramTagItem(InstagramItem):
    pass


class InstagramImageItem(InstagramItem):
    images = scrapy.Field()


class InstagramFollowersItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follow_id = scrapy.Field()
    follow_name = scrapy.Field()


class InstagramFollowsItem(scrapy.Item):
    _id = scrapy.Field()
    user_id = scrapy.Field()
    user_name = scrapy.Field()
    follow_id = scrapy.Field()
    follow_name = scrapy.Field()
