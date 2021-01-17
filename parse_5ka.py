import requests
import json
import time
from pathlib import Path


class ParseError(Exception):
    def __init__(self, text):
        self.text = text


class Parse5ka:
    _headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    _params = {'records_per_page': 50, 'categories': 000}

    def __init__(self, start_url: str, result_path: Path):
        self.start_url = start_url
        self.result_path = result_path

    @staticmethod
    def __get_response(url: str, *args, **kwargs) -> requests.Response:
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

    def run(self):
        for product in self.parse(self.start_url):
            file_path = self.result_path.joinpath(f'{product["id"]}.json')
            self.save(product, file_path)

    def parse(self, url: str) -> dict:
        while url:
            response = self.__get_response(url, params=self._params, headers=self._headers)
            data = response.json()
            url = data['next']
            for product in data['results']:
                yield product

    @staticmethod
    def save(data: dict, file_path: Path):
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    url = 'https://5ka.ru/api/v2/special_offers/'
    result_path = Path(__file__).parent.joinpath('products')
    parser = Parse5ka(url, result_path)
    parser.run()
