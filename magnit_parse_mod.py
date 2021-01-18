import os
import time
import datetime
import requests
import bs4
import pymongo
from urllib.parse import urljoin
from dotenv import load_dotenv


class ParseError(Exception):
    def __init__(self, text):
        self.text = text


class MagnitParser:
    def __init__(self, start_url, data_client):
        self.start_url = start_url
        self.data_client = data_client
        self.data_base = self.data_client['parsing_2021']

    @staticmethod
    def _get_response(url, *args, **kwargs):
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

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
            'promo_name': lambda tag: tag.find('div', attrs={'class': 'card-sale__header'}).text,
            'product_name': lambda tag: tag.find('div', attrs={'class': 'card-sale__title'}).text,
            'old_price': lambda tag: float(
                f"{(tag.find('div', attrs={'class': 'label__price_old'}).find('span', attrs={'class': 'label__price-integer'}).text)}.{(tag.find('div', attrs={'class': 'label__price_old'}).find('span', attrs={'class': 'label__price-decimal'}).text)}"),
            'new_price': lambda tag: float(
                f"{(tag.find('div', attrs={'class': 'label__price_new'}).find('span', attrs={'class': 'label__price-integer'}).text)}.{(tag.find('div', attrs={'class': 'label__price_new'}).find('span', attrs={'class': 'label__price-decimal'}).text)}"),
            'image_url': lambda tag: urljoin('https://magnit.ru/',
                                             tag.find('img', attrs={'class': 'lazy'}).attrs.get('data-src')),
            'date_from': lambda tag: self.date_time(tag.find('div', attrs={'class': 'card-sale__date'}).find('p').text),
            'date_to': lambda tag: self.date_time(
                tag.find('div', attrs={'class': 'card-sale__date'}).find_all('p')[1].text)
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

    def date_time(self, date):
        dict_month = {'январ': '01', 'феврал': '02', 'март': '03', 'апрел': '04', 'ма': '05', 'июн': '06', 'июл': '07',
                      'август': '08', 'сентябр': '09', 'октябр': '10', 'ноябр': '11', 'декабр': '12'}

        if "с" in date:
            lst = date.replace("с ", "").split(' ')
        else:
            lst = date.replace("до ", "").split(' ')

        for key, value in dict_month.items():
            if key in lst[1]:
                lst[1] = value
                break

        return datetime.datetime(year=2021, month=int(lst[1]), day=int(lst[0]), hour=0, minute=0, second=0,
                                 microsecond=0)


if __name__ == '__main__':
    load_dotenv('.env')
    data_base_url = os.getenv('DATA_BASE_URL')
    data_client = pymongo.MongoClient(data_base_url)
    url = 'https://magnit.ru/promo/?geo=moskva'
    parser = MagnitParser(url, data_client)
    parser.run()
