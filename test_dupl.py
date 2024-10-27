import requests
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import mysql.connector
from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import tldextract
load_dotenv()
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Подключение к БД
conn_1 = mysql.connector.connect(
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
conn_2 = mysql.connector.connect(
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

if conn_1.is_connected() and conn_2.is_connected():
    cursor_1 = conn_1.cursor()
    cursor_2 = conn_2.cursor()
    print('Есть подключение к БД:')

    cursor_1.execute(
        "SELECT RESOURCE_ID, RESOURCE_URL "
        "FROM resource "
        "WHERE status = %s",
        ('spider_scrapy',)
    )
    resources = cursor_1.fetchall()
else:
    print('ошибка')

def extract_domain(url):
    try:
        extracted = tldextract.extract(url)
        # Если поддомен существует и не равен 'www', включаем его в результат
        if extracted.subdomain and extracted.subdomain != 'www':
            return f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}"
        else:
            return f"{extracted.domain}.{extracted.suffix}"
    except Exception as e:
        print(f"Ошибка при парсинге URL {url}: {e}")
        return None

print(extract_domain('http://bbn.ee.feedsportal.com/c/33176/f/545933/index.rss'))