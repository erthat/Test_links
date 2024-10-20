FROM python:3.11-slim

# Устанавливаем зависимости для MySQL и другие утилиты
RUN apt-get update && apt-get install -y \
    wget \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Добавляем репозиторий Google для получения последней версии Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | tee /etc/apt/sources.list.d/google-chrome.list

# Устанавливаем последнюю версию Google Chrome
RUN apt-get update && apt-get install -y \
    google-chrome-stable

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем зависимости проекта
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# Запуск Scrapy
CMD ["python", "main.py"]
