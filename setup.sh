#!/bin/bash

# Music Streaming Analytics Platform Setup Script
echo "🎵 Setting up Music Streaming Analytics Platform..."

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p analytics/dbt/models/{staging,marts}
mkdir -p analytics/expectations/{expectations,checkpoints,uncommitted}
mkdir -p orchestration/airflow/{dags,logs,plugins}
mkdir -p apps/{producer,spark}
mkdir -p dashboards/powerbi
mkdir -p infra/helm
mkdir -p docs

# Set executable permissions
chmod +x setup.sh

# Check if Docker is running
echo "🐳 Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if virtual environment exists and activate it
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r apps/spark/requirements.txt
pip install -r orchestration/airflow/requirements.txt

# Install dbt
echo "🔧 Installing dbt..."
pip install dbt-postgres==1.7.4

# Start Docker services
echo "🚀 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
docker-compose ps

# Create Kafka topic
echo "📡 Creating Kafka topic..."
docker exec kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --topic music.play_events \
    --partitions 3 \
    --replication-factor 1 \
    --if-not-exists

# Initialize Airflow database
echo "🗄️ Initializing Airflow database..."
docker exec airflow-webserver airflow db init

# Create Airflow admin user
echo "👤 Creating Airflow admin user..."
docker exec airflow-webserver airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

# Initialize dbt project
echo "🏗️ Initializing dbt project..."
cd analytics/dbt
dbt debug --profiles-dir .
cd ../..

echo "✅ Setup complete!"
echo ""
echo "🌐 Access URLs:"
echo "  Kafka UI:      http://localhost:8080"
echo "  Airflow:       http://localhost:8085 (admin/admin)"
echo "  Jupyter Lab:   http://localhost:8888 (token: music-analytics)"
echo "  Schema Registry: http://localhost:8081"
echo ""
echo "🎯 Next steps:"
echo "  1. Run the producer: cd apps/producer && python producer.py"
echo "  2. Run the consumer: cd apps/producer && python consumer.py"
echo "  3. Run Spark analytics: cd apps/spark && python batch_processor.py"
echo "  4. View Kafka messages in UI: http://localhost:8080"
echo "  5. Check Airflow DAGs: http://localhost:8085"
echo ""
echo "🛑 To stop all services: docker-compose down"
