import scrapy
import json
import datetime
from ..loaders import InstagramTagLoader, InstagramImageLoader
from ..items import InstagramFollowersItem, InstagramFollowsItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    json_url = 'https://www.instagram.com/graphql/query/?query_hash='
    query_hash = {
        "posts": "56a7068fea504063273cc2120ffd54f3",
        "tag_posts": "9b498c08113f1e09617a1703c22b2f32",
        "followers": "5aefa9893005572d237da5068082d8d5",
        "following": "3dec7e2c57367ef3da3d987d89f9dbc8",
    }
    dict_json_url = {
        "tag_name": "",
        "first": 100,
        "after": "",
    }
    variables_followers = {
        "id": "",
        "include_reel": True,
        "fetch_mutual": False,
        "first": 100,
        "after": "",
    }
    full_name = ""

    def __init__(self, login, password, *args, **kwargs):
        self.tags = ["python", "программирование", "developers"]
        self.followers = ["silkirumyul"]
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
                # for tag in self.tags:
                #     yield response.follow(f"/explore/tags/{tag}/", callback=self.tag_parse)
                for follower in self.followers:
                    yield response.follow(f"/{follower}/", callback=self.followers_parse)
                    # yield response.follow(f"/{follower}/", callback=self.following_parse)

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        graphql = js_data["entry_data"]["TagPage"][0]["graphql"]["hashtag"]
        # date_parse = datetime.datetime.utcnow()
        # data = {
        #     "id": graphql["hashtag"]["id"],
        #     "name": graphql["hashtag"]["name"],
        #     "profile_pic_url": graphql["hashtag"]["profile_pic_url"],
        # }
        # yield from self.instagram_tag(date_parse, data, response)
        yield from self.get_tag_posts(graphql, response)

    def followers_parse(self, response):
        js_data = self.js_data_extract(response)
        graphql = js_data["entry_data"]["ProfilePage"][0]["graphql"]
        self.full_name = graphql["user"]["full_name"]
        self.variables_followers["id"] = graphql["user"]["id"]
        self.variables_followers["after"] = graphql["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        dict_json = json.dumps(self.variables_followers)
        url = f"{self.json_url}{self.query_hash['followers']}&variables={dict_json}"
        yield response.follow(url, callback=self.followers_api_parse)

    def following_parse(self, response):
        js_data = self.js_data_extract(response)
        graphql = js_data["entry_data"]["ProfilePage"][0]["graphql"]
        self.full_name = graphql["user"]["full_name"]
        self.variables_followers["id"] = graphql["user"]["id"]
        self.variables_followers["after"] = graphql["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
        dict_json = json.dumps(self.variables_followers)
        url = f"{self.json_url}{self.query_hash['following']}&variables={dict_json}"
        yield response.follow(url, callback=self.following_api_parse)

    @staticmethod
    def instagram_tag(date_parse, data, response):
        loader = InstagramTagLoader(response=response)
        loader.add_value("data", data)
        loader.add_value("date", date_parse)
        yield loader.load_item()

    # def tag_api_parse(self, response):
    #     yield from self.get_tag_posts(response.json()["data"]["hashtag"], response)

    def followers_api_parse(self, response):
        yield from self.get_tag_posts(response.json()["data"]["user"], response)

    def following_api_parse(self, response):
        yield from self.get_following(response.json()["data"]["user"], response)

    def get_tag_posts(self, graphql, response):
        # if graphql["edge_hashtag_to_media"]["page_info"]["has_next_page"]:
        #     name = graphql["name"]
        #     end_cursor = graphql["edge_hashtag_to_media"]["page_info"]["end_cursor"]
        #     self.dict_json_url["tag_name"] = name
        #     self.dict_json_url["after"] = end_cursor
        #     dict_json = json.dumps(self.dict_json_url)
        #     url = f"{self.json_url}{self.query_hash['tag_posts']}&variables={dict_json}"
        #     yield response.follow(url, callback=self.tag_api_parse)
        # yield from self.images_parse(graphql["edge_hashtag_to_top_posts"]["edges"], response)

        if graphql["edge_followed_by"]["page_info"]["has_next_page"]:
            self.variables_followers["after"] = graphql["edge_followed_by"]["page_info"]["end_cursor"]
            dict_json = json.dumps(self.variables_followers)
            url = f"{self.json_url}{self.query_hash['followers']}&variables={dict_json}"
            yield response.follow(url, callback=self.followers_api_parse)
        yield from self.follower_parse(graphql["edge_followed_by"]["edges"])

    def get_following(self, graphql, response):
        if graphql["edge_followed_by"]["page_info"]["has_next_page"]:
            self.variables_followers["after"] = graphql["edge_followed_by"]["page_info"]["end_cursor"]
            dict_json = json.dumps(self.variables_followers)
            url = f"{self.json_url}{self.query_hash['following']}&variables={dict_json}"
            yield response.follow(url, callback=self.following_api_parse)
        yield from self.follow_parse(graphql["edge_followed_by"]["edges"])

    def follower_parse(self, edges):
        for user in edges:
            yield InstagramFollowersItem(
                follow_id=user["node"]["id"],  # этот пользователь
                follow_name=user["node"]["full_name"],
                user_id=self.variables_followers["id"],  # на этого пользователя
                user_name=self.full_name,
            )

    def follow_parse(self, edges):
        for user in edges:
            yield InstagramFollowsItem(
                user_id=self.variables_followers["id"],  # этот пользователь
                user_name=self.full_name,
                follow_id=user["node"]["id"],  # на этого пользователя
                follow_name=user["node"]["full_name"],
            )

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
