import random

from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import logging
from selenium.webdriver.remote.remote_connection import LOGGER as selenium_logger
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
import gc

# Устанавливаем уровень логирования для Selenium на INFO
selenium_logger.setLevel(logging.INFO)


class SeleniumMiddleware:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Настройки для безголового браузера (headless mode)
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920x1080")

        chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36")
        service = Service(ChromeDriverManager().install())
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1,
        })
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Proxy;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Object;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_JSON;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                    '''
        })
        self.driver.implicitly_wait(5)


        # self.driver = webdriver.Chrome(options=chrome_options)

    def process_request(self, request, spider):
        location = {
            "latitude": 43.2220,
            "longitude": 76.8512,
            "accuracy": 100
        }

        # Обрабатываем только те запросы, которые требуют динамической загрузки

        self.driver.get(request.url)
        spider.logger.info(f"Parsing: {request.url}")
        self.driver.execute_script(
            f"navigator.geolocation.getCurrentPosition = function(success) {{ success({json.dumps(location)}); }};")

        wait_time = random.uniform(5, 10)
        self.logger.info(f"Waiting for {wait_time:.2f} seconds before getting page source.")
        time.sleep(wait_time)
        # Получаем HTML-код страницы
        body = self.driver.page_source

        links = [elem.get_attribute('href') for elem in self.driver.find_elements(By.XPATH, "//a")]
        # max_links_to_show = 3
        # if len(links) > max_links_to_show:
        #     spider.logger.info(
        #         f"Found links: {links[:max_links_to_show]}... and {len(links) - max_links_to_show} more links.")
        # else:
        #     spider.logger.info(f"Found links: {links}")

        # Возвращаем `HtmlResponse`, который будет передан в `parse` метод паука
        self.driver.delete_all_cookies()
        self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        # self.driver.close()
        return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)


    def process_response(self, request, response, spider):
        # Простой метод, который возвращает ответ без изменений
        return response

    def spider_closed(self):
        # Закрываем браузер при завершении работы паука
        self.driver.delete_all_cookies()
        self.driver.execute_cdp_cmd('Network.clearBrowserCache', {})
        self.driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
        self.driver.close()
        self.driver.quit()
        gc.collect()
