
FROM python:3.11-slim

WORKDIR /app


COPY . .


RUN pip install --no-cache-dir -r requirements.txt


ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Открываем порт
EXPOSE 8080

# Запускаем приложение
CMD ["flask", "run"]
