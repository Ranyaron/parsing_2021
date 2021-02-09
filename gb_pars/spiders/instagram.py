import scrapy
import json
import datetime
from ..loaders import InstagramTagLoader, InstagramImageLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    json_url = 'https://www.instagram.com/graphql/query/?query_hash='
    query_hash = {
        "posts": "56a7068fea504063273cc2120ffd54f3",
        "tag_posts": "9b498c08113f1e09617a1703c22b2f32",
    }
    dict_json_url = {
        "tag_name": "",
        "first": 1,
        "after": "",
    }

    def __init__(self, login, password, *args, **kwargs):
        self.tags = ["python", "программирование", "developers"]
        self.login = login
        self.enc_password = password
        super().__init__(*args, **kwargs)

    def parse(self, response, **kwargs):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self.login_url,
                method="POST",
                callback=self.parse,
                formdata={
                    "username": self.login,
                    "enc_password": self.enc_password,
                },
                headers={
                    "X-CSRFToken": js_data["config"]["csrf_token"],
                },
            )
        except AttributeError:
            if response.json().get("authenticated"):
                for tag in self.tags:
                    yield response.follow(f"/explore/tags/{tag}/", callback=self.tag_parse)

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        hashtag = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]
        date_parse = datetime.datetime.utcnow()
        data = {
            "id": hashtag["id"],
            "name": hashtag["name"],
            "profile_pic_url": hashtag["profile_pic_url"],
        }
        yield from self.instagram_tag(date_parse, data, response)
        yield from self.get_tag_posts(hashtag, response)

    @staticmethod
    def instagram_tag(date_parse, data, response):
        loader = InstagramTagLoader(response=response)
        loader.add_value("data", data)
        loader.add_value("date", date_parse)
        yield loader.load_item()

    def tag_api_parse(self, response):
        yield from self.get_tag_posts(response.json()["data"]["hashtag"], response)

    def get_tag_posts(self, hashtag, response):
        if hashtag["edge_hashtag_to_media"]["page_info"]["has_next_page"]:
            name = hashtag["name"]
            end_cursor = hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"]
            self.dict_json_url["tag_name"] = name
            self.dict_json_url["after"] = end_cursor
            dict_json = json.dumps(self.dict_json_url)
            url = f"{self.json_url}{self.query_hash['tag_posts']}&variables={dict_json}"
            yield response.follow(url, callback=self.tag_api_parse)
        yield from self.images_parse(hashtag["edge_hashtag_to_top_posts"]["edges"], response)

    @staticmethod
    def images_parse(edges, response):
        loader = InstagramImageLoader(response=response)
        date_parse = datetime.datetime.utcnow()
        for image in edges:
            loader.add_value("images", image["node"]["display_url"])
            loader.add_value("data", image["node"])
        loader.add_value("date", date_parse)
        yield loader.load_item()

    @staticmethod
    def js_data_extract(response) -> dict:
        script = response.xpath("//body/script[contains(text(), 'csrf_token')]/text()").get()
        return json.loads(script.replace("window._sharedData = ", "", 1)[:-1])
