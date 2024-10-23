import pytz
import mysql.connector
from OpenSSL.rand import status
from scrapy.spiders import Spider, Rule
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
from dateparser import parse
import time
from dotenv import load_dotenv
import emoji
import re
from lxml.html import fromstring
import bs4
import os
from mysql.connector import Error
import unicodedata
from datetime import datetime, timedelta
from urllib.parse import urlparse, urlunparse
import urllib.parse
from scrapy import Request
import scrapy


load_dotenv()
class Selenium_Spider(scrapy.Spider):
    name = 'selenium_spider'
    custom_settings = { }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_1 = None
        self.cursor_1 = None
        self.conn_2 = None
        self.cursor_2 = None
        self.start_urls = []


        try:
            self.conn_1 = mysql.connector.connect(
                host=os.getenv("DB_HOST_1"),
                user=os.getenv("DB_USER_1"),
                password=os.getenv("DB_PASSWORD_1"),
                database=os.getenv("DB_DATABASE_1"),
                port=os.getenv("DB_PORT_1"),
                charset='utf8mb4',
                collation='utf8mb4_general_ci',
                connection_timeout=300,
                autocommit=True

            )
            # подключение к таблице temp_items и temp_items_link
            self.conn_2 = mysql.connector.connect(
                host=os.getenv("DB_HOST_2"),
                user=os.getenv("DB_USER_2"),
                password=os.getenv("DB_PASSWORD_2"),
                database=os.getenv("DB_DATABASE_2"),
                port=os.getenv("DB_PORT_2"),
                charset='utf8mb4',
                collation='utf8mb4_general_ci',
                connection_timeout=300,
                autocommit=True

            )

            if self.conn_1.is_connected() and self.conn_2.is_connected():
                self.cursor_1 = self.conn_1.cursor()
                self.cursor_2 = self.conn_2.cursor()
                self.logger.info('Есть подключение к БД:')

                self.cursor_1.execute(
                    "SELECT RESOURCE_ID, RESOURCE_NAME, RESOURCE_URL, top_tag, bottom_tag, title_cut, date_cut, convert_date, block_page, middle_tag "
                    "FROM resource "
                    "WHERE status = %s ",
                    ('SP',)
                )

                self.resources = self.cursor_1.fetchall()
                self.start_urls = [resource[2].split(',')[0].strip() for resource in self.resources]
                self.resource_map = {resource[0]: resource for resource in self.resources}


            else:
                self.log("No resources found, spider will close.")
                self.crawler.engine.close_spider(self, f'Нету данных в бд ')

        except Error as e:
            self.log(f"Error connecting to MySQL: {e}")
            self.logger.info('Нет подключение к БД')
            # Переключаемся на временный паук чтобы закрыть паука и запустить через 30 мин
            self.name = "temporary_spider"
            self.start_urls = ["http://example.com"]
            self.rules = ()

    def start_requests(self):
        # Здесь вы можете получить ссылки из вашей базы данных
        links = self.start_urls

        for link in links:
            yield Request(link, self.parse_start_url)

    def parse_start_url(self, response):
        """Функция для парсинга стартовой страницы и начала парсинга ссылок"""

        current_domain = urlparse(response.url).hostname.replace('www.', '')
        resource_info = next(
            (res for res in self.resource_map.values() if
             urlparse(res[2].split(',')[0].strip()).hostname.replace('www.', '') == current_domain),
            None
        )
        resource_id = resource_info[0]
        status = response.status
        current_url = response.request.url
        redirect_url = response.request.url if response.url != response.request.url else None

        self.store_news(resource_id, current_url, status, redirect_url)

    def store_news(self, resource_id, current_url, status, redirect_url):
        # Проверка соединения перед выполнением операций
        if not self.conn_2.is_connected():
            try:
                self.logger.warning("Соединение с базой данных потеряно, пытаемся переподключиться...")
                self.conn_2.reconnect(attempts=3, delay=5)
                self.logger.info("Соединение восстановлено")
            except mysql.connector.Error as err:
                self.logger.warning(f"Ошибка переподключения: {err}")
                return  # Прекращаем выполнение, если не удалось переподключиться
        self.cursor_2.execute(
            "SELECT COUNT(*) FROM test_link WHERE resource_id = %s",
            (resource_id,)
        )
        (count,) = self.cursor_2.fetchone()

        if count == 0:
            self.cursor_2.execute(
                "INSERT INTO test_link (resource_id, current_url, status, redirect_url, Selenium) VALUES (%s, %s, %s, %s)",
                (resource_id, current_url, status, redirect_url)
            )
            self.conn_2.commit()
        else:
        # Если ссылка уже существует
            self.logger.info(f'ошибка {resource_id}')

    def close(self, reason):
        if self.cursor_2:
            self.cursor_2.close()
        if self.conn_2:
            self.conn_2.close()



