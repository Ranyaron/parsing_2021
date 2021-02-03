import scrapy
from ..loaders import HhruAdsLoader, HhruAuthorLoader, HhruAuthorAdsLoader


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://rostov.hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113'
    ]

    # ссылка для подставления id автора (компании) для поиска всех его объявлений
    url_author_vacancies = "https://hh.ru/search/vacancy?st=searchVacancy&from=employerPage&employer_id="

    xpath_query = {
        "pagination": "//span/a[@data-qa='pager-page']",
        "ads": "//span/a[@data-qa='vacancy-serp__vacancy-title']",
    }

    data_ad_xpath = {
        "title": "//h1/text()",  # название вакансии
        "salary": "//p[@class='vacancy-salary']",  # оклад (строкой от до или просто сумма)
        "description": "//div[@class='vacancy-branded-user-content'] | //div[@class='vacancy-description']",  # описание вакансии
        "skills": "//body",  # ключевые навыки - в виде списка названий
        "url_author": "//div[contains(@class, 'vacancy-company__details')]/a",  # ссылка на автора вакансии
    }

    data_author_xpath = {
        "name": "//h1/span//text()",  # название
        "link": "//div[contains(@class, 'employer-sidebar-content')]/a/@href",  # сайт ссылка (если есть)
        "areas": "//div[contains(text(), 'Сферы деятельности')]/../p/text()",  # сферы деятельности (списком)
        "description": "//div[@class='g-user-content'] | //div[@class='tmpl_hh-wrapper'] | //div[@class='company-description']",  # описание
    }

    def parse(self, response, **kwargs):
        pagination_links = response.xpath(self.xpath_query["pagination"])
        yield from self.gen_task(response, pagination_links, self.parse)
        ads_links = response.xpath(self.xpath_query["ads"])
        yield from self.gen_task(response, ads_links, self.ads_parse)

    def ads_parse(self, response):
        loader = HhruAdsLoader(response=response)
        for key, selector in self.data_ad_xpath.items():
            loader.add_xpath(key, selector)
        loader.add_value("url", response.url)
        yield loader.load_item()

        url_author_link = response.xpath(self.data_ad_xpath["url_author"])
        yield from self.gen_task(response, url_author_link, self.author_parse)

    """
    Собираем данные со страницы компании,
    которая опубликовала данное объявление
    """
    def author_parse(self, response):
        loader = HhruAuthorLoader(response=response)
        for key, selector in self.data_author_xpath.items():
            loader.add_xpath(key, selector)
        loader.add_value("url", response.url)
        yield loader.load_item()

        # берем id компании
        id_author = ''.join(i for i in response.url if i.isdigit())
        # соединяем ссылку поиска объявлений с id компании
        url_author_vacancies_link = f"{self.url_author_vacancies}{id_author}"
        yield from self.gen_author_vacancies(response, url_author_vacancies_link, self.author_ads_parse)

    def author_ads_parse(self, response):
        pagination_links = response.xpath(self.xpath_query["pagination"])
        yield from self.gen_task(response, pagination_links, self.author_ads_parse)
        ads_links = response.xpath(self.xpath_query["ads"])
        yield from self.gen_task(response, ads_links, self.author_vacancies_parse)

    """
    Собираем данные по объявлениям одной компании,
    заходя на каждую страницу объявления
    """
    def author_vacancies_parse(self, response):
        loader = HhruAuthorAdsLoader(response=response)
        for key, selector in self.data_ad_xpath.items():
            loader.add_xpath(key, selector)
        loader.add_value("url", response.url)
        yield loader.load_item()

    @staticmethod
    def gen_task(response, list_links, callback):
        for link in list_links:
            yield response.follow(link.attrib.get("href"), callback=callback)

    @staticmethod
    def gen_author_vacancies(response, list_links, callback):
        yield response.follow(list_links, callback=callback)
