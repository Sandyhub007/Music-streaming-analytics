from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json

def create_spark_session():
    """Create Spark session for batch processing"""
    return SparkSession.builder \
        .appName("MusicBatchAnalytics") \
        .config("spark.sql.adaptive.enabled", "true") \
        .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
        .getOrCreate()

def generate_sample_data(spark):
    """Generate sample music streaming data for testing"""
    import random
    from datetime import datetime, timedelta
    
    # Sample data
    users = [f"user_{i}" for i in range(1, 21)]
    songs = [f"song_{i}" for i in range(1, 51)]
    artists = [f"artist_{i}" for i in range(1, 11)]
    actions = ["play", "pause", "skip", "complete"]
    devices = ["mobile", "web", "tv", "desktop"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    
    # Generate 1000 sample events
    sample_events = []
    base_time = datetime.now() - timedelta(hours=1)
    
    for i in range(1000):
        event_time = base_time + timedelta(seconds=random.randint(0, 3600))
        event = {
            "event_id": f"event_{i}",
            "event_ts": event_time.isoformat(),
            "user_id": random.choice(users),
            "song_id": random.choice(songs),
            "artist_id": random.choice(artists),
            "action": random.choice(actions),
            "device": random.choice(devices),
            "location": random.choice(locations)
        }
        sample_events.append(event)
    
    # Create DataFrame
    df = spark.createDataFrame(sample_events)
    df = df.withColumn("event_ts", to_timestamp(col("event_ts")))
    
    return df

def analyze_music_data(df):
    """Perform batch analytics on music streaming data"""
    
    print("=== MUSIC STREAMING ANALYTICS REPORT ===\n")
    
    # 1. Total events by action type
    print("1. Events by Action Type:")
    action_summary = df.groupBy("action") \
        .count() \
        .orderBy(desc("count"))
    action_summary.show()
    
    # 2. Most popular songs (by play count)
    print("2. Top 10 Most Played Songs:")
    popular_songs = df.filter(col("action") == "play") \
        .groupBy("song_id", "artist_id") \
        .count() \
        .withColumnRenamed("count", "play_count") \
        .orderBy(desc("play_count")) \
        .limit(10)
    popular_songs.show()
    
    # 3. Most active users
    print("3. Top 10 Most Active Users:")
    active_users = df.groupBy("user_id") \
        .agg(
            count("*").alias("total_events"),
            countDistinct("song_id").alias("unique_songs"),
            countDistinct("action").alias("unique_actions")
        ) \
        .orderBy(desc("total_events")) \
        .limit(10)
    active_users.show()
    
    # 4. Device usage patterns
    print("4. Usage by Device Type:")
    device_usage = df.groupBy("device") \
        .agg(
            count("*").alias("total_events"),
            countDistinct("user_id").alias("unique_users")
        ) \
        .withColumn("avg_events_per_user", round(col("total_events") / col("unique_users"), 2)) \
        .orderBy(desc("total_events"))
    device_usage.show()
    
    # 5. Geographic distribution
    print("5. Geographic Distribution:")
    geo_distribution = df.groupBy("location") \
        .agg(
            count("*").alias("total_events"),
            countDistinct("user_id").alias("unique_users"),
            countDistinct("song_id").alias("unique_songs")
        ) \
        .orderBy(desc("total_events"))
    geo_distribution.show()
    
    # 6. Hourly activity pattern
    print("6. Hourly Activity Pattern:")
    hourly_activity = df.withColumn("hour", hour("event_ts")) \
        .groupBy("hour") \
        .count() \
        .orderBy("hour")
    hourly_activity.show(24)
    
    # 7. User session analysis
    print("7. User Session Analysis:")
    session_analysis = df.groupBy("user_id") \
        .agg(
            min("event_ts").alias("first_event"),
            max("event_ts").alias("last_event"),
            count("*").alias("total_events")
        ) \
        .withColumn("session_duration_minutes", 
                   round((unix_timestamp("last_event") - unix_timestamp("first_event")) / 60, 2)) \
        .filter(col("session_duration_minutes") > 0) \
        .orderBy(desc("session_duration_minutes")) \
        .limit(10)
    session_analysis.show()
    
    # 8. Skip rate analysis
    print("8. Skip Rate Analysis by Song:")
    skip_analysis = df.groupBy("song_id", "artist_id") \
        .agg(
            sum(when(col("action") == "play", 1).otherwise(0)).alias("plays"),
            sum(when(col("action") == "skip", 1).otherwise(0)).alias("skips"),
            sum(when(col("action") == "complete", 1).otherwise(0)).alias("completes")
        ) \
        .filter(col("plays") > 0) \
        .withColumn("skip_rate", round(col("skips") / col("plays") * 100, 2)) \
        .withColumn("completion_rate", round(col("completes") / col("plays") * 100, 2)) \
        .orderBy(desc("skip_rate")) \
        .limit(10)
    skip_analysis.show()

def main():
    """Main execution function"""
    print("Starting Music Streaming Batch Analytics...")
    
    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    try:
        # Generate sample data
        print("Generating sample music streaming data...")
        df = generate_sample_data(spark)
        
        print(f"Generated {df.count()} sample events")
        print("Sample data schema:")
        df.printSchema()
        
        # Perform analytics
        analyze_music_data(df)
        
        # Optional: Save results to parquet files
        print("\nSaving analytics results...")
        
        # Save popular songs
        popular_songs = df.filter(col("action") == "play") \
            .groupBy("song_id", "artist_id") \
            .count() \
            .withColumnRenamed("count", "play_count")
        
        popular_songs.write \
            .mode("overwrite") \
            .parquet("/tmp/music_analytics/popular_songs")
        
        # Save user activity
        user_activity = df.groupBy("user_id") \
            .agg(
                count("*").alias("total_events"),
                countDistinct("song_id").alias("unique_songs")
            )
        
        user_activity.write \
            .mode("overwrite") \
            .parquet("/tmp/music_analytics/user_activity")
        
        print("Analytics results saved to /tmp/music_analytics/")
        
    except Exception as e:
        print(f"Error in batch processing: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
