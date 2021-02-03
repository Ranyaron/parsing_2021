import re
from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from .items import AutoyoulaItem, HhruAdsItem, HhruAuthorItem, HhruAuthorAdsItem
from itemloaders.processors import TakeFirst, MapCompose


def clear_unicode(item):
    return item.replace("\u2009", "")


def get_author_id(item):
    re_pattern = re.compile(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar")
    result = re.findall(re_pattern, item)
    return result


def get_specifications(item):
    tag = Selector(text=item)
    name = tag.xpath("//div[@class='AdvertSpecs_label__2JHnS']/text()").get()
    value = tag.xpath("//div[@class='AdvertSpecs_data__xK2Qx']//text()").get()
    return {name: value}


def get_salary(item):
    tag = Selector(text=item)
    result = tag.xpath("//span[contains(@class, 'bloko-header-2')]/text()").getall()
    return "".join(result).replace("\xa0", " ")


def get_description(item):
    tag = Selector(text=item)
    result = tag.xpath("//p//text() | //div//p//text() | //div//div//p//text() | //div//text()").getall()
    return "".join(result).replace("\xa0", "").replace("   ", " ").replace("  ", " ")


def get_skills(item):
    tag = Selector(text=item)
    skills = tag.xpath("//div[contains(@class, 'bloko-tag-list')]//span/text()").getall()
    return [skills]


def get_url_author(item):
    tag = Selector(text=item)
    return urljoin("https://hh.ru/", tag.xpath("//a/@href").get())


def get_are(item):
    result = item.split(', ')
    return [result]


def flat_dict(items: list) -> dict:
    result = {}
    for itm in items:
        result.update(itm)
    return result


class AutoyoulaLoader(ItemLoader):
    default_item_class = AutoyoulaItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    price_in = MapCompose(clear_unicode, float)
    price_out = TakeFirst()
    author_in = MapCompose(get_author_id, lambda a_id: urljoin("https://youla.ru/user/", a_id))
    author_out = TakeFirst()
    description = TakeFirst()
    specifications_in = MapCompose(get_specifications)
    specifications_out = flat_dict


class HhruAdsLoader(ItemLoader):
    default_item_class = HhruAdsItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(get_salary)
    salary_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    skills_in = MapCompose(get_skills)
    skills_out = TakeFirst()
    url_author_in = MapCompose(get_url_author)
    url_author_out = TakeFirst()


class HhruAuthorLoader(ItemLoader):
    default_item_class = HhruAuthorItem
    url_out = TakeFirst()
    name_out = TakeFirst()
    link_out = TakeFirst()
    areas_in = MapCompose(get_are)
    areas_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    vacancies_out = TakeFirst()


class HhruAuthorAdsLoader(ItemLoader):
    default_item_class = HhruAuthorAdsItem
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(get_salary)
    salary_out = TakeFirst()
    description_in = MapCompose(get_description)
    description_out = TakeFirst()
    skills_in = MapCompose(get_skills)
    skills_out = TakeFirst()
    url_author_in = MapCompose(get_url_author)
    url_author_out = TakeFirst()
