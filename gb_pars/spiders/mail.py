import scrapy


class MailSpider(scrapy.Spider):
    name = 'mail'
    allowed_domains = ['https://e.mail.ru/inbox/']
    start_urls = ['https://e.mail.ru/inbox/']

    def parse(self, response):
        pass
