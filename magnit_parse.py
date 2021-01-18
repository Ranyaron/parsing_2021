import os
import requests
import bs4
import pymongo
from urllib.parse import urljoin
from dotenv import load_dotenv


class MagnitParser:
    def __init__(self, start_url, data_client):
        self.start_url = start_url
        self.data_client = data_client
        self.data_base = self.data_client['parsing_2021']

    @staticmethod
    def _get_response(url, *args, **kwargs):
        # todo надо обработать ошибки запросов и сделать повторный запрос
        response = requests.get(url, *args, **kwargs)
        return response

    @staticmethod
    def _get_soup(response):
        return bs4.BeautifulSoup(response.text, 'lxml')

    def run(self):
        for product in self.parse(self.start_url):
            self.save(product)

    def parse(self, url) -> dict:
        soup = self._get_soup(self._get_response(url))
        catalog_main = soup.find('div', attrs={'class': 'сatalogue__main'})
        for product_tag in catalog_main.find_all('a', attrs={'class': 'card-sale'}):
            yield self._get_product_data(product_tag)

    @property
    def data_template(self):
        return {
            'url': lambda tag: urljoin(self.start_url, tag.attrs.get('href')),
            'title': lambda tag: tag.find('div', attrs={'class': 'card-sale__title'}).text
        }

    def _get_product_data(self, product_tag: bs4.Tag) -> dict:
        data = {}
        for key, pattern in self.data_template.items():
            try:
                data[key] = pattern(product_tag)
            except AttributeError:
                pass
        return data

    def save(self, data):
        collection = self.data_base['magnit']
        collection.insert_one(data)
        pass


if __name__ == '__main__':
    load_dotenv('.env')
    data_base_url = os.getenv('DATA_BASE_URL')
    data_client = pymongo.MongoClient(data_base_url)
    url = 'https://magnit.ru/promo/?geo=moskva'
    parser = MagnitParser(url, data_client)
    parser.run()
