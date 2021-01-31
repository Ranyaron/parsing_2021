import scrapy
from ..loaders import HhruLoader
from scrapy.http import Response

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://rostov.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113'
    ]

    xpath_query = {
        "pagination": "//span/a[@data-qa='pager-page']",
        "ads": "//span/a[@data-qa='vacancy-serp__vacancy-title']",
    }

    data_xpath = {
        "title": "//h1/text()",  # название вакансии
        "salary": "//p[@class='vacancy-salary']",  # оклад (строкой от до или просто сумма)
        # "description": "//div[@class='vacancy-description']//div/p/text() | //div[@class='vacancy-description']//div/p/span/text() | //div[@class='vacancy-description']//div/p/strong/text()",  # описание вакансии
        # "description": "//div[@class='vacancy-description']//div/p | //div[@class='vacancy-description']//div/p/span | //div[@class='vacancy-description']//div/p/strong",  # описание вакансии
        "description": "//body",  # описание вакансии
        # "skills": "//div[contains(@class, 'bloko-tag-list')]//span/text()",  # ключевые навыки - в виде списка названий
        "skills": "//body",  # ключевые навыки - в виде списка названий
        "url_author": "//div[contains(@class, 'vacancy-company__details')]/a/@href",  # ссылка на автора вакансии
    }

    def parse(self, response, **kwargs):
        pagination_links = response.xpath(self.xpath_query["pagination"])
        yield from self.gen_task(response, pagination_links, self.parse)
        ads_links = response.xpath(self.xpath_query["ads"])
        yield from self.gen_task(response, ads_links, self.ads_parse)

    def ads_parse(self, response):
        loader = HhruLoader(response=response)
        for key, selector in self.data_xpath.items():
            loader.add_xpath(key, selector)
        loader.add_value("url", response.url)
        yield loader.load_item()

    @staticmethod
    def gen_task(response, list_links, callback):
        for link in list_links:
            yield response.follow(link.attrib.get("href"), callback=callback)
        print(1)


# Перейти на страницу автора вакансии,
# собрать данные:

# 1. Название
# 2. сайт ссылка (если есть)
# 3. сферы деятельности (списком)
# 4. Описание

# Обойти и собрать все вакансии данного автора.
