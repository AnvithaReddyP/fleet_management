FROM python:3.11-slim

# Install system dependencies, curl, and add MariaDB repository for ODBC drivers
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    curl \
    gnupg \
    && curl -sS https://downloads.mariadb.com/MariaDB/mariadb_repo_setup | bash \
    && apt-get update && apt-get install -y \
    odbc-mariadb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT app:app