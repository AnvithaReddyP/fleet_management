FROM python:3.11-slim

# Install system dependencies and curl
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Download and install MySQL Connector/ODBC for Linux (added -L flag for redirects)
RUN curl -OL https://dev.mysql.com/get/Downloads/Connector-ODBC/8.0/mysql-connector-odbc-8.0.36-linux-glibc2.28-x86-64bit.tar.gz \
    && tar -xvf mysql-connector-odbc-8.0.36-linux-glibc2.28-x86-64bit.tar.gz \
    && cp mysql-connector-odbc-8.0.36-linux-glibc2.28-x86-64bit/bin/* /usr/local/bin/ \
    && cp mysql-connector-odbc-8.0.36-linux-glibc2.28-x86-64bit/lib/* /usr/local/lib/ \
    && rm -rf mysql-connector-odbc-8.0.36*

# Register the driver for Linux
RUN echo "[MySQL ODBC 8.0 Unicode Driver]\nDescription=MySQL ODBC Driver\nDriver=/usr/local/lib/libmyodbc8w.so\nSetup=/usr/local/lib/libmyodbc8S.so\nFileUsage=1\n" >> /etc/odbcinst.ini

# Set working directory
WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port and run using gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]