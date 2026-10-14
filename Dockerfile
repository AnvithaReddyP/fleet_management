FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libmyodbc \
    && rm -rf /var/lib/apt/lists/*

# Register the exact driver name for Linux unixODBC
RUN echo "[MySQL ODBC 26.7(w) Driver]" >> /etc/odbcinst.ini \
    && echo "Description=MySQL ODBC 26.7 Driver" >> /etc/odbcinst.ini \
    && echo "Driver=/usr/lib/x86_64-linux-gnu/odbc/libmyodbc8w.so" >> /etc/odbcinst.ini \
    && echo "UsageCount=1" >> /etc/odbcinst.ini

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD gunicorn --bind 0.0.0.0:$PORT app:app