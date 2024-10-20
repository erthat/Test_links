from twisted.internet import asyncioreactor
asyncioreactor.install()
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from selenium_spider.spiders.selenium_spider import Selenium_Spider
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
import logging
from logging.handlers import RotatingFileHandler
import os
import shutil

log_file = 'logs/logi.log'
handler = RotatingFileHandler(
    log_file,           # Имя файла логов
    mode='a',           # Режим добавления ('a'), чтобы не перезаписывать сразу
    maxBytes=25*1024*1024,  # Максимальный размер файла (в байтах), например, 5 МБ
    backupCount=1       # Количество резервных копий логов (если установить 0, то старый файл будет перезаписываться)
)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        handler,
        logging.StreamHandler()
        # Используем RotatingFileHandler
    ]
)

spider_resources = {}


logging.basicConfig(
    level=logging.INFO,  # Устанавливаем уровень логирования
    format='%(levelname)s: %(message)s',
)


def clean_tmp_folder():
    tmp_dir = '/tmp'
    exclude_dirs = ['systemd-', '.X11-unix', '.ICE-unix', '.XIM-unix', '.font-unix']

    for filename in os.listdir(tmp_dir):
        file_path = os.path.join(tmp_dir, filename)

        # Пропустить системные файлы
        if any(filename.startswith(excl) for excl in exclude_dirs):
            continue

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


@inlineCallbacks
def crawl():
    runner = CrawlerRunner(get_project_settings())
    yield runner.crawl(Selenium_Spider)

    # clean_tmp_folder()
    reactor.callLater(600, crawl)  # Запланировать следующий запуск через 15 минут

# Запуск первого цикла
crawl()

# Запуск основного цикла событий Twisted
reactor.run()