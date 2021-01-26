import scrapy
from scrapy.http import Response


class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']
    css_query = {
        "brand": "div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
    }

    data_query = {
        "title": "div.AdvertCard_advertTitle__1S1Ak::text",
        "price": "div.AdvertCard_price__3dDCr::text",
        "description": "div.AdvertCard_descriptionInner__KnuRi::text",
    }

    @staticmethod
    def gen_task(response, list_links, callback):
        for link in list_links:
            yield response.follow(link.attrib.get("href"), callback=callback)

    def parse(self, response: Response):
        yield from self.gen_task(response, response.css(self.css_query["brand"]), self.brand_parse)

    def brand_parse(self, response: Response):
        yield from self.gen_task(response, response.css(self.css_query["pagination"]), self.brand_parse)
        yield from self.gen_task(response, response.css(self.css_query["ads"]), self.ads_parse)

    def ads_parse(self, response: Response):
        data = {}
        for name, query in self.data_query.items():
            data[name] = response.css(query).get()
        print(1)
