# Use official lightweight Python image
FROM python:3.11-slim

# Install system dependencies, curl, and ODBC libraries
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Download and install the official MySQL ODBC driver for Debian/Ubuntu
RUN curl -sSL https://dev.mysql.com/get/mysql-apt-config_0.8.29-1_all.deb -o mysql-apt-config.deb \
    && echo "mysql-apt-config mysql-apt-config/select-server select none" | debconf-set-selections \
    && DEBIAN_FRONTEND=noninteractive dpkg -i mysql-apt-config.deb \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-odbc \
    && rm mysql-apt-config.deb

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