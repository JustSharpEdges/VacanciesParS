# Используем официальный образ Python в качестве базового
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы приложения в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем переменные окружения
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["flask", "run"]
