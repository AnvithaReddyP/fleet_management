FROM python:3.11-slim

# Install system dependencies and ODBC drivers for Linux
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    curl \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install the Microsoft/MySQL ODBC package repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update

# Install unixodbc-bin and driver components
RUN apt-get update && apt-get install -y --no-install-recommends \
    odbcinst \
    unixodbc \
    libodbc1

# Set working directory
WORKDIR /app

# Copy requirements and install python packages (including pyodbc)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port and run using gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]