# 🎵 Music Streaming Analytics Platform

A comprehensive real-time analytics platform for music streaming data, built with modern data engineering tools and best practices.

## 🚀 Features

- **Real-time Data Streaming**: Kafka-based event streaming with realistic music listening simulation
- **Stream Processing**: Apache Spark for real-time analytics and batch processing
- **Data Transformation**: dbt models for data warehouse transformations
- **Data Quality**: Great Expectations for data validation and monitoring
- **Orchestration**: Apache Airflow for workflow management
- **Visualization**: PowerBI dashboard integration
- **Monitoring**: Real-time monitoring dashboard for streaming metrics
- **Infrastructure**: Docker-compose for local development, Kubernetes-ready

## 📊 Architecture

```
[Music Producer] → [Kafka] → [Spark Streaming] → [Data Warehouse]
                      ↓            ↓                    ↓
                 [Monitoring]  [Analytics]         [dbt Models]
                                   ↓                    ↓
                              [Airflow] ← [Great Expectations]
                                   ↓
                            [PowerBI Dashboards]
```

## 🛠️ Tech Stack

- **Streaming**: Apache Kafka, Kafka UI, Schema Registry
- **Processing**: Apache Spark (PySpark), Jupyter Lab
- **Orchestration**: Apache Airflow
- **Data Quality**: Great Expectations
- **Transformation**: dbt (data build tool)
- **Storage**: PostgreSQL (dev), configurable for production
- **Monitoring**: Custom Python monitoring dashboard
- **Infrastructure**: Docker, Docker Compose
- **Languages**: Python 3.11+

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Git

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Sandyhub007/Music-streaming-analytics.git
   cd Music-streaming-analytics
   ```

2. Run the setup script:
   ```bash
   ./setup.sh
   ```

3. Access the services:
   - **Kafka UI**: http://localhost:8080
   - **Airflow**: http://localhost:8085 (admin/admin)
   - **Jupyter Lab**: http://localhost:8888 (token: music-analytics)

### Running the Pipeline

1. **Start the producer** (generates realistic music streaming events):
   ```bash
   cd apps/producer
   python producer.py
   ```

2. **Monitor real-time metrics**:
   ```bash
   cd apps/producer
   python monitoring.py
   ```

3. **Run Spark analytics**:
   ```bash
   cd apps/spark
   python batch_processor.py
   ```

## 📁 Project Structure

```
music-streaming-analytics/
├── apps/
│   ├── producer/           # Kafka producers and monitoring
│   └── spark/              # Spark streaming and batch jobs
├── analytics/
│   ├── dbt/                # Data transformation models
│   └── expectations/       # Data quality expectations
├── orchestration/
│   └── airflow/            # Workflow orchestration
├── dashboards/
│   └── powerbi/            # Visualization dashboards
├── infra/
│   └── helm/               # Kubernetes deployment configs
├── docs/                   # Documentation
└── docker-compose.yml     # Local development environment
```

## 📈 Analytics Capabilities

### Real-time Metrics
- Events per second processing rates
- User activity patterns
- Popular songs and artists
- Device usage distribution
- Geographic listening patterns

### Batch Analytics
- User engagement analysis
- Song popularity metrics
- Skip rate and completion analysis
- Hourly activity patterns
- Session duration analysis

### Data Quality Monitoring
- Schema validation
- Data freshness checks
- Anomaly detection
- Business rule validation

## 🔧 Configuration

### Environment Variables
- `KAFKA_BOOTSTRAP_SERVERS`: Kafka cluster endpoints
- `POSTGRES_CONNECTION`: Database connection string
- `AIRFLOW_HOME`: Airflow configuration directory

### Scaling
- Kafka partitions: Configurable for horizontal scaling
- Spark executors: Adjustable based on processing needs
- dbt threads: Configurable for transformation parallelism

## 🧪 Testing

Run data quality tests:
```bash
cd analytics/dbt
dbt test --profiles-dir .
```

Run Great Expectations validation:
```bash
cd analytics/expectations
great_expectations checkpoint run music_events_checkpoint
```

## 🚦 Production Deployment

### Kubernetes
Helm charts are provided in `infra/helm/` for production deployment.

### Data Warehouse Integration
Configure dbt profiles for your data warehouse:
- Snowflake
- BigQuery
- Redshift
- PostgreSQL

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For questions and support:
- Create an issue in the GitHub repository
- Check the documentation in the `docs/` folder

## 🔮 Roadmap

- [ ] Machine learning models for recommendation systems
- [ ] Real-time alerting and anomaly detection
- [ ] Advanced streaming analytics with complex event processing
- [ ] Integration with cloud data warehouses
- [ ] Advanced visualization with custom dashboards
- [ ] A/B testing framework integration
