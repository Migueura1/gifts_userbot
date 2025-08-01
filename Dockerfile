FROM python:3.11-slim

# Устанавливаем системные зависимости, нужные для сборки TgCrypto и других пакетов
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    python3-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Создаем каталоги для логов
RUN mkdir -p /app/bot/logs

# Указываем команду запуска
CMD ["python", "app/main.py"]
