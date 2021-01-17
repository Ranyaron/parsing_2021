import requests

url = 'https://5ka.ru/api/v2/special_offers/'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

# ?categories=&ordering=&page=2&price_promo__gte=&price_promo__lte=&records_per_page=12&search=&store=
params = {'records_per_page': 50}

response: requests.Response = requests.get(url, headers=headers)

with open('5ka.ru.html', 'w', encoding='UTF-8') as file:
    file.write(response.text)

print(1)
