import scrapy
import json
from ..loaders import InstagramLoader


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    json_url = 'https://www.instagram.com/graphql/query/?query_hash=9b498c08113f1e09617a1703c22b2f32&variables='
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
        yield from self.get_tag_posts(hashtag, response)

    def get_tag_posts(self, hashtag, response):
        if hashtag["edge_hashtag_to_media"]["page_info"]["has_next_page"]:
            name = hashtag["name"]
            end_cursor = hashtag["edge_hashtag_to_media"]["page_info"]["end_cursor"]
            self.dict_json_url["tag_name"] = name
            self.dict_json_url["after"] = end_cursor
            dict_json = json.dumps(self.dict_json_url)
            url = f"{self.json_url}{dict_json}"
            yield response.follow(url, callback=self.get_tag_posts(response.json()["data"]["hashtag"], response))
        yield from self.images_parse(hashtag["edge_hashtag_to_top_posts"]["edges"], response)

    def images_parse(self, edges, response):
        loader = InstagramLoader(response=response)
        # for key, selector in self.data_xpath.items():
        #     loader.add_xpath(key, selector)

        # js_data = json.loads(response.xpath("//body/p/text()").get())
        # js_images = js_data["data"]["hashtag"]["edge_hashtag_to_top_posts"]["edges"]
        list_urls_images = []
        for image in edges:
            # list_urls_images.append(image["node"]["display_url"])
            loader.add_value("images", image["node"]["display_url"])
        loader.add_value("url", response.url)
        # loader.add_value("images", list_urls_images)
        yield loader.load_item()

    @staticmethod
    def js_data_extract(response) -> dict:
        script = response.xpath("//body/script[contains(text(), 'csrf_token')]/text()").get()
        return json.loads(script.replace("window._sharedData = ", "", 1)[:-1])
