import scrapy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class ZillowSpider(scrapy.Spider):
    name = 'zillow'
    allowed_domains = ['www.zillow.com']
    start_urls = ['https://www.zillow.com/san-francisco-ca/']
    xpath_selectors = {
        'pagination': '//div[@class="search-pagination"]/nav[@aria-label="Pagination"]/ul/li/a/@href',
        'ads': '//article[contains(@class, "list-card")]//a[contains(@class, "list-card-link")]/@href',
    }
    # browser = webdriver.Firefox()

    @staticmethod
    def _get_page_response(response, urls_list, callback):
        for link in urls_list:
            yield response.follow(link, callback=callback)

    def parse(self, response):
        yield from self._get_page_response(
            response,
            response.xpath(self.xpath_selectors['pagination']),
            self.parse,
        )

        yield from self._get_page_response(
            response,
            response.xpath(self.xpath_selectors['ads']),
            self.ads_parse,
        )

    def ads_parse(self, response):
        self.browser.get(response.url)
        media_col = self.browser.find_element_by_xpath('//div[contains(@class, "ds-media-col")]')
        len_photos = len(media_col.find_elements_by_xpath('//picture[contains(@class, "media-stream-photo")]'))
        while True:
            for _ in range(5):
                media_col.send_keys(Keys.PAGE_DOWN)
            photos = media_col.find_elements_by_xpath('//picture[contains(@class, "media-stream-photo")]')
            if len_photos == len(photos):
                break
