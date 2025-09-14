FROM apache/airflow:2.7.1-python3.11

# Switch to root to install system packages
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install additional Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Copy custom configurations
COPY airflow.cfg /opt/airflow/airflow.cfg
