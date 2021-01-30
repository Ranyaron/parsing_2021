import os
import re
import pymongo
import scrapy
from scrapy.http import Response
from dotenv import load_dotenv
from urllib.parse import urljoin

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['https://auto.youla.ru/']

    load_dotenv('.env')
    data_base_url = os.getenv('DATA_BASE_URL')
    data_client = pymongo.MongoClient(data_base_url)
    data_base = data_client['parsing_2021']
    collection = data_base[name]

    css_query = {
        "brand": "div.ColumnItemList_container__5gTrc a.blackLink",
        "pagination": "div.Paginator_block__2XAPy a.Paginator_button__u1e7D",
        "ads": "article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu",
    }

    data_query = {
        "title": "div.AdvertCard_advertTitle__1S1Ak::text",
        "price": "div.AdvertCard_price__3dDCr::text",
        "photos": "img.PhotoGallery_photoImage__2mHGn::attr(src)",  # Список фото объявления (ссылки)
        "specifications": [
            "div.AdvertSpecs_row__ljPcX div.AdvertSpecs_label__2JHnS::text",
            "div.AdvertSpecs_row__ljPcX div.AdvertSpecs_data__xK2Qx::text, div.AdvertSpecs_row__ljPcX div.AdvertSpecs_data__xK2Qx a::text"
        ],  # Список характеристик
        "description": "div.AdvertCard_descriptionInner__KnuRi::text",
        "author": "script::text",  # Ссылка на автора объявления
        # "telephone": ""  # Телефон
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
            if name == "photos":
                data[name] = response.css(query).getall()
            elif name == "specifications":
                query_lst_0 = response.css(query[0]).getall()
                query_lst_1 = response.css(query[1]).getall()
                data[name] = dict(zip(query_lst_0, query_lst_1))
            elif name == "author":
                script = response.css(query).getall()
                result_re = re.findall(r"youlaId%22%2C%22([0-9a-zA-Z]+)%22%2C%22avatar", script[8])
                url_user = "https://youla.ru/user/"
                data[name] = urljoin(url_user, result_re[0])
            else:
                data[name] = response.css(query).get()

        self.collection.insert_one(data)
