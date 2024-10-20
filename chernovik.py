# driver = get_driver()
# # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
# #     'source': '''
# #         delete window.cdc._adoQpoasnfa76pfcZLmcfl_Array;
# #         delete window.cdc._adoQpoasnfa76pfcZLmcfl_Promise;
# #         delete window.cdc._adoQpoasnfa76pfcZLmcfl_Symbol;
# #         '''
# # })
# try:
#     driver.get(url)
#
#     # Ожидание для обхода проверки Cloudflare
#     time.sleep(5)  # Задержка для имитации поведения пользователя
#
#     # # Явное ожидание и взаимодействие с элементами
#     # wait = WebDriverWait(driver, 10)
#     # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "header")))
#     html = driver.page_source
#
#
# finally:
#     driver.quit()
#
#     import scrapy
#     from scrapy.http import HtmlResponse
#
#
#     class Selenium_Spider(scrapy.Spider):
#         name = 'selenium_spider'
#
#         def __init__(self, html='', *args, **kwargs):
#             super(Selenium_Spider, self).__init__(*args, **kwargs)
#             self.html = html
#
#         def start_requests(self):
#             # Используем `HtmlResponse` для парсинга HTML
#             response = HtmlResponse(url='dummy_url', body=self.html, encoding='utf-8')
#             yield from self.parse(response)
#
#         def parse(self, response):
#             # Пример: извлечение всех ссылок из HTML
#             links = response.css('a::attr(href)').getall()
#             for link in links:
#                 yield {'link': link}
#
#
#
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings
# from selenium_spider.spiders.selenium_spider import Selenium_Spider
# from selenium_spider.selenium import get_html
#
# def main():
#     url = 'https://www.inform.kz/'
#     html = get_html(url)
#
#     process = CrawlerProcess(get_project_settings())
#     process.crawl(Selenium_Spider, html=html)
#     process.start()
#
# if __name__ == '__main__':
#     main()
#
# import undetected_chromedriver as uc
# from selenium.webdriver.chrome.options import Options
# import time
#
# def get_html(url):
#     options = Options()
#     options.add_argument("--headless=new")  # Запуск в фоновом режиме (без GUI)
#     options.add_argument("--disable-blink-features=AutomationControlled")  # Отключение обнаружения автоматизации
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--window-size=1920x1080")  # Стандартный размер окна
#     options.add_argument(
#         "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36")
#
#     driver = uc.Chrome(options=options)
#     try:
#         driver.get(url)
#         time.sleep(5)  # Ожидание для полной загрузки страницы
#         html = driver.page_source
#     finally:
#         driver.quit()
#     return html
#
