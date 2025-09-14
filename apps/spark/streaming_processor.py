from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

def create_spark_session():
    """Create Spark session with Kafka integration"""
    return SparkSession.builder \
        .appName("MusicStreamingAnalytics") \
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def define_schema():
    """Define schema for music streaming events"""
    return StructType([
        StructField("event_id", StringType(), True),
        StructField("event_ts", TimestampType(), True),
        StructField("user_id", StringType(), True),
        StructField("song_id", StringType(), True),
        StructField("artist_id", StringType(), True),
        StructField("action", StringType(), True),
        StructField("device", StringType(), True),
        StructField("location", StringType(), True)
    ])

def process_streaming_data(spark):
    """Main streaming processing logic"""
    
    # Read from Kafka
    kafka_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "music.play_events") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Parse JSON data
    schema = define_schema()
    
    parsed_df = kafka_df.select(
        from_json(col("value").cast("string"), schema).alias("data"),
        col("timestamp").alias("kafka_timestamp")
    ).select("data.*", "kafka_timestamp")
    
    # Convert event_ts string to timestamp
    events_df = parsed_df.withColumn(
        "event_ts", 
        to_timestamp(col("event_ts"), "yyyy-MM-dd'T'HH:mm:ss.SSSSSS")
    )
    
    # Real-time analytics
    
    # 1. Count events by action type (windowed aggregation)
    action_counts = events_df \
        .withWatermark("event_ts", "10 seconds") \
        .groupBy(
            window(col("event_ts"), "30 seconds", "10 seconds"),
            col("action")
        ) \
        .count() \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("action"),
            col("count")
        )
    
    # 2. Popular songs (most played in last 5 minutes)
    popular_songs = events_df \
        .filter(col("action") == "play") \
        .withWatermark("event_ts", "10 seconds") \
        .groupBy(
            window(col("event_ts"), "5 minutes", "1 minute"),
            col("song_id"),
            col("artist_id")
        ) \
        .count() \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("song_id"),
            col("artist_id"),
            col("count").alias("play_count")
        )
    
    # 3. User activity patterns
    user_activity = events_df \
        .withWatermark("event_ts", "10 seconds") \
        .groupBy(
            window(col("event_ts"), "2 minutes", "30 seconds"),
            col("user_id"),
            col("device")
        ) \
        .agg(
            count("*").alias("total_events"),
            countDistinct("song_id").alias("unique_songs"),
            collect_set("action").alias("actions")
        ) \
        .select(
            col("window.start").alias("window_start"),
            col("window.end").alias("window_end"),
            col("user_id"),
            col("device"),
            col("total_events"),
            col("unique_songs"),
            col("actions")
        )
    
    return action_counts, popular_songs, user_activity, events_df

def start_streaming_queries(action_counts, popular_songs, user_activity, events_df):
    """Start streaming queries with different output modes"""
    
    # Console output for action counts
    action_query = action_counts.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime="10 seconds") \
        .queryName("action_counts") \
        .start()
    
    # Console output for popular songs
    songs_query = popular_songs.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime="30 seconds") \
        .queryName("popular_songs") \
        .start()
    
    # Console output for user activity
    user_query = user_activity.writeStream \
        .outputMode("update") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime="20 seconds") \
        .queryName("user_activity") \
        .start()
    
    # Raw events to console (for debugging)
    raw_query = events_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", False) \
        .trigger(processingTime="5 seconds") \
        .queryName("raw_events") \
        .start()
    
    return [action_query, songs_query, user_query, raw_query]

def main():
    """Main execution function"""
    print("Starting Music Streaming Analytics with Spark...")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Process streaming data
        action_counts, popular_songs, user_activity, events_df = process_streaming_data(spark)
        
        # Start streaming queries
        queries = start_streaming_queries(action_counts, popular_songs, user_activity, events_df)
        
        print("Streaming queries started. Waiting for data...")
        print("Available queries:")
        for query in queries:
            print(f"- {query.name}: {query.id}")
        
        # Wait for termination
        for query in queries:
            query.awaitTermination()
            
    except Exception as e:
        print(f"Error in streaming application: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
