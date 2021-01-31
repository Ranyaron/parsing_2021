import re
from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from .items import AutoyoulaItem, HhruItem
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
    salary = Selector(text=item)
    result = salary.xpath("//span[contains(@class, 'bloko-header-2')]/text()").getall()
    return "".join(result).replace("\xa0", " ")


def get_description(item):
    description = Selector(text=item)
    description = description.xpath("//div[@class='vacancy-description']//div/p/text() | //div[@class='vacancy-description']//div/p/span/text() | //div[@class='vacancy-description']//div/p/strong/text()").getall()
    # description = description.getall()
    join_description = "".join(description).replace("\xa0", " ")
    result = re.findall("[А-Я][^А-Я]*", join_description)
    return " ".join(result)
    # return [result]


def get_skills(item):
    skills = Selector(text=item)
    skills = skills.xpath("//div[contains(@class, 'bloko-tag-list')]//span/text()").getall()
    # return ", ".join(skills)
    return [skills]


def get_url_author(item):
    return urljoin("https://rostov.hh.ru/", item)


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


class HhruLoader(ItemLoader):
    default_item_class = HhruItem
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
