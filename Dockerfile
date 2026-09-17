# Use official Python image
FROM python:3.11-slim

# Install system dependencies and ODBC drivers
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    default-libmysqlclient-dev \
    build-essential \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install the MySQL ODBC Driver repository/package
RUN apt-get update && apt-get install -y odbc-mysql

# Set working directory
WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port and run the app using gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]