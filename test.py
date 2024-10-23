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

def remove_after_domain(url):
    parsed_url = urlparse(url)
    # Формируем URL без пути
    return f"{parsed_url.scheme}://{parsed_url.hostname}"


def extract_domain(url):
    try:
        extracted = tldextract.extract(url)
        return f"{extracted.domain}.{extracted.suffix}"  # Формируем домен второго уровня и суффикс
    except Exception as e:
        print(f"Ошибка при парсинге URL {url}: {e}")
        return None

# Функция для запроса через requests
def check_url_via_requests(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.history:
            original_domain = extract_domain(url)
            final_domain = extract_domain(response.url)
            if original_domain != final_domain:
                return 300, response.url
            else:
                return response.status_code, response.url
        else:
            return response.status_code, None

    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return 999, url

# Функция для запроса через Selenium
def check_url_via_selenium(url):
    try:
        service = Service(ChromeDriverManager().install())
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.137 Safari/537.36")
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.geolocation": 1,
            "profile.default_content_setting_values.notifications": 1,
        })
        driver = webdriver.Chrome(service=service,options=chrome_options)
        driver.set_page_load_timeout(20)

        try:
            driver.get(url)
            current_url = driver.current_url
            # Проверяем, если страница загрузилась (например, страница не пустая)
            if len(driver.page_source) > 0:
                status = 200  # Страница успешно загрузилась
            else:
                status = 404  # Если страница пустая, возвращаем 404
        except Exception as e:
            # Если возникла ошибка во время загрузки страницы
            # print(f"Timeout or error loading {url}: {e}")
            status = 404
            current_url = url

        driver.quit()  # Закрываем браузер
        return status, current_url

    except Exception as e:
        print(f"Error with Selenium for {url}: {e}")
        return 999, url

def save_to_db(resource_id, url, status, redirect_url, selenium_used):
    cursor_2.execute("SELECT 1 FROM test_link WHERE resource_id = %s", (resource_id,))
    if cursor_2.fetchone() is None:
        cursor_2.execute(
            "INSERT INTO test_link (resource_id, current_url, status, redirect_url, Selenium) VALUES (%s, %s, %s, %s, %s)",
            (resource_id, url, status, redirect_url, selenium_used)
        )
        conn_2.commit()
        print(f'Запись добавлена для resource_id: {resource_id}')
    else:
        print(f'resource_id существует {resource_id}')

# Основной цикл обработки
for resource_id, url in resources:
    cursor_2.execute("SELECT 1 FROM test_link WHERE resource_id = %s", (resource_id,))
    if cursor_2.fetchone() is None:

        url = url.split(',')[0].strip()
        url =  remove_after_domain(url)
        # Пробуем через requests
        status, redirect_url = check_url_via_requests(url)
        selenium_used = 'no'
        if status == 200 or status == 300 or status == 404:
            save_to_db(resource_id, url, status, redirect_url, selenium_used)
        else:
            # Если ошибка или редирект, пробуем через Selenium
            status, redirect_url = check_url_via_selenium(url)
            selenium_used = 'yes'
            save_to_db(resource_id, url, status, redirect_url, selenium_used)
    else:
        print(f'resource_id существует {resource_id}')

    # Закрытие соединения с БД
cursor_1.close()
conn_1.close()
cursor_2.close()
conn_2.close()