FROM python:3.11-slim

# Install system dependencies required for pyodbc and ODBC drivers
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libmyodbc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT app:app