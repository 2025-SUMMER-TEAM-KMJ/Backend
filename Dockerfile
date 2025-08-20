FROM python:3.11-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y libsqlite3-dev sqlite3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 8765

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8765", "--log-level", "debug"]
