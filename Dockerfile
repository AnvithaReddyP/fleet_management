FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Install build dependencies for pyodbc and the MariaDB ODBC driver (fully compatible with MySQL / Aiven)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    odbc-mariadb \
    && rm -rf /var/lib/apt/lists/*

# Register driver aliases so unixODBC recognizes both 'MariaDB Unicode' and 'MySQL ODBC 26.7 Unicode Driver'
RUN echo "[MySQL ODBC 26.7 Unicode Driver]" >> /etc/odbcinst.ini \
    && echo "Description=MariaDB Connector/ODBC (MySQL Compatible)" >> /etc/odbcinst.ini \
    && echo "Driver=/usr/lib/x86_64-linux-gnu/odbc/libmaodbc.so" >> /etc/odbcinst.ini \
    && echo "UsageCount=1" >> /etc/odbcinst.ini

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT app:app