import os
import time
import requests
import bs4
import database_mod
import datetime
from urllib.parse import urljoin
from dotenv import load_dotenv


class GbParse:
    def __init__(self, start_url, db):
        self.db = db
        self.start_url = start_url
        self.done_url = set()
        self.tasks = [self.parse_task(self.start_url, self.pag_parse)]
        self.done_url.add(self.start_url)

    @staticmethod
    def _get_response(*args, **kwargs):
        try:
            time.sleep(0.1)
            return requests.get(*args, **kwargs)
        except requests.RequestException:
            time.sleep(0.5)
            pass

    def _get_soup(self, *args, **kwargs):
        response = self._get_response(*args, **kwargs)
        return bs4.BeautifulSoup(response.text, "lxml")

    def parse_task(self, url, callback):
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)

        return task

    def run(self):
        for task in self.tasks:
            result = task()
            if result:
                self.save(result)

    def pag_parse(self, url, soup):
        self.create_parse_tasks(url, soup.find("ul", attrs={
            "class": "gb__pagination"
        }).find_all("a"), self.pag_parse)
        self.create_parse_tasks(url, soup.find("div", attrs={
            "class": "post-items-wrapper"
        }).find_all("a", attrs={
            "class": "post-item__title"
        }), self.post_parse)

    def create_parse_tasks(self, url, tag_list, callback):
        for a_tag in tag_list:
            a_url = urljoin(url, a_tag.get("href"))
            if a_url not in self.done_url:
                task = self.parse_task(a_url, callback)
                self.tasks.append(task)
                self.done_url.add(a_url)

    def post_parse(self, url, soup):
        post_data = {
            "title": soup.find("h1", attrs={"class": "blogpost-title"}).text,
            "url": url,
            "img_url": soup.find("img").get("src"),
            "date_time": datetime.datetime.strptime(
                soup.find("time").get("datetime")[:-6].replace("T", " "),
                "%Y-%m-%d %H:%M:%S"
            )
        }

        author_tag_name = soup.find("div", attrs={"itemprop": "author"})
        author = {
            "name": author_tag_name.text,
            "url": urljoin(url, author_tag_name.parent.get("href"))
        }

        tags_a = soup.find("article", attrs={
                               "class": "blogpost__article-wrapper"
                           }).find_all("a", attrs={"class": "small"})
        tags = [{"url": urljoin(url, tag.get("href")), "name": tag.text} for tag in tags_a]

        commentable_id = int(soup.find("div", attrs={
                                           "class": "referrals-social-buttons-small-wrapper"
                                       }).get("data-minifiable-id"))  # получаем id статьи
        url_comment = [
            "https://geekbrains.ru/api/v2/comments?commentable_type=Post&commentable_id=",
            "&order=desc"
        ]
        soup_comment = self._get_response(
            f"{url_comment[0]}{commentable_id}{url_comment[1]}"
        ).json()
        comments = [
            {
                "name": com["comment"]["user"]["full_name"],
                "text": com["comment"]["body"],
                "url": com["comment"]["user"]["url"]
            } for com in soup_comment
        ]

        return {
            "post_data": post_data,
            "author": author,
            "tags": tags,
            "comments": comments
        }

    def save(self, data):
        self.db.create_post(data)


if __name__ == "__main__":
    load_dotenv(".env")
    db = database_mod.Database(os.getenv("SQL_DB_URL"))
    parser = GbParse("https://geekbrains.ru/posts", db)
    parser.run()
