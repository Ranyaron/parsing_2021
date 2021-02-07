import os
from dotenv import load_dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from gb_pars.spiders.autoyoula import AutoyoulaSpider
from gb_pars.spiders.hhru import HhruSpider
from gb_pars.spiders.instagram import InstagramSpider

if __name__ == "__main__":
    load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("gb_pars.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    # crawler_process.crawl(AutoyoulaSpider)
    # crawler_process.crawl(HhruSpider)
    crawler_process.crawl(InstagramSpider, login=os.getenv("LOGIN"), password=os.getenv("PASSWORD"))
    crawler_process.start()
