# Spark Processing for Music Streaming Analytics

This directory contains Spark applications for processing music streaming data in both batch and streaming modes.

## Files

- `streaming_processor.py` - Real-time streaming analytics using Spark Structured Streaming
- `batch_processor.py` - Batch analytics for historical data analysis
- `requirements.txt` - Python dependencies for Spark applications

## Features

### Streaming Analytics (`streaming_processor.py`)
- Real-time processing of Kafka music events
- Windowed aggregations for action counts
- Popular songs tracking (5-minute windows)
- User activity patterns analysis
- Watermark-based late data handling

### Batch Analytics (`batch_processor.py`)
- Comprehensive historical data analysis
- Popular songs and artists identification
- User behavior analysis
- Device usage patterns
- Geographic distribution analysis
- Hourly activity patterns
- Skip rate and completion rate analysis

## Running the Applications

### Prerequisites
1. Activate the virtual environment:
   ```bash
   source ../../venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Batch Processing
```bash
python batch_processor.py
```
This will generate sample data and run comprehensive analytics.

### Streaming Processing
1. Start Kafka (if not already running)
2. Start the producer:
   ```bash
   cd ../producer
   python producer.py
   ```
3. In another terminal, start the streaming processor:
   ```bash
   python streaming_processor.py
   ```

## Output
- Batch processor saves results to `/tmp/music_analytics/`
- Streaming processor outputs real-time analytics to console
- Both applications provide detailed analytics reports

## Analytics Included

1. **Action Counts** - Events by type (play, pause, skip, complete)
2. **Popular Songs** - Most played tracks with play counts
3. **User Activity** - Most active users and their engagement
4. **Device Usage** - Usage patterns across different devices
5. **Geographic Distribution** - Events by location
6. **Temporal Patterns** - Hourly activity analysis
7. **Session Analysis** - User session duration and behavior
8. **Skip Rate Analysis** - Song popularity and completion rates

## Next Steps
- Integrate with data warehouse (e.g., Snowflake, BigQuery)
- Add machine learning models for recommendations
- Implement alerting for anomaly detection
- Add more sophisticated windowing strategies
