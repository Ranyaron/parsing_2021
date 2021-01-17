import requests
import json
import time
from pathlib import Path


class ParseError(Exception):
    def __init__(self, text):
        self.text = text


class Parse5ka:
    _headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}
    _params_categories = {'records_per_page': 50}
    codes = []
    category = []
    _params = {'records_per_page': 50, 'categories': 000}

    def __init__(self, url_categories: str, url_special_offers: str, result_path: Path):
        self.url_categories = url_categories
        self.url_special_offers = url_special_offers
        self.result_path = result_path

    @staticmethod
    def _get_response(url: str, *args, **kwargs) -> requests.Response:
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

    def parse(self, url: str) -> dict:
        x = 0
        for c in self.codes:
            self._params['categories'] = c
            r = True
            while r:
                response = self._get_response(url, params=self._params, headers=self._headers)
                data = response.json()
                r = data['next']
                d = dict(self.category[x])
                d.update({"products": data['results']})
                print(d)
                file_path = self.result_path.joinpath(f'{d["parent_group_name"]}.json')
                self.save(d, file_path)
            x += 1

    def parse_categories(self, url: str) -> dict:
        response_categories = self._get_response(url, params=self._params_categories, headers=self._headers)
        self.category = response_categories.json()
        return self.category

    def code_categories(self, url: str):
        code_categories = self.parse_categories(url)
        for i in range(len(code_categories)):
            for key, value in code_categories[i].items():
                if key == 'parent_group_code':
                    self.codes.append(int(value))

    @staticmethod
    def save(data: dict, file_path: Path):
        with file_path.open('w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False)


if __name__ == '__main__':
    url_categories = 'https://5ka.ru/api/v2/categories/'
    url_special_offers = 'https://5ka.ru/api/v2/special_offers/'
    result_path = Path(__file__).parent.joinpath('products_mod')
    parser = Parse5ka(url_categories, url_special_offers, result_path)
    parser.code_categories(url_categories)
    parser.parse(url_special_offers)
