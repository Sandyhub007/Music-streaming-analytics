#!/usr/bin/env python3
"""
Music Streaming Analytics - Real-time Monitoring Dashboard
Provides real-time insights into the streaming data pipeline
"""

import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading
from kafka import KafkaConsumer
import signal
import sys

class StreamingMonitor:
    def __init__(self):
        self.consumer = KafkaConsumer(
            "music.play_events",
            bootstrap_servers="localhost:9092",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="monitoring-consumer"
        )
        
        self.running = True
        self.events_processed = 0
        self.start_time = datetime.now()
        
        # Metrics tracking
        self.recent_events = deque(maxlen=1000)  # Last 1000 events
        self.user_activity = defaultdict(int)
        self.song_popularity = defaultdict(int)
        self.device_stats = defaultdict(int)
        self.action_stats = defaultdict(int)
        self.location_stats = defaultdict(int)
        
        # Time-based metrics
        self.hourly_events = defaultdict(int)
        self.events_per_minute = deque(maxlen=60)  # Last 60 minutes
        
    def process_event(self, event):
        """Process a single streaming event and update metrics"""
        self.events_processed += 1
        self.recent_events.append(event)
        
        # Update metrics
        self.user_activity[event['user_id']] += 1
        self.action_stats[event['action']] += 1
        self.device_stats[event['device']] += 1
        self.location_stats[event['location']] += 1
        
        if event['action'] == 'play':
            self.song_popularity[event['song_id']] += 1
        
        # Time-based metrics
        event_time = datetime.fromisoformat(event['event_ts'].replace('Z', '+00:00'))
        hour_key = event_time.strftime('%H:00')
        self.hourly_events[hour_key] += 1
        
    def calculate_metrics(self):
        """Calculate real-time metrics"""
        now = datetime.now()
        uptime = now - self.start_time
        
        # Events per second
        eps = self.events_processed / uptime.total_seconds() if uptime.total_seconds() > 0 else 0
        
        # Recent activity (last 100 events)
        recent_100 = list(self.recent_events)[-100:] if len(self.recent_events) >= 100 else list(self.recent_events)
        
        # Top users, songs, etc.
        top_users = sorted(self.user_activity.items(), key=lambda x: x[1], reverse=True)[:5]
        top_songs = sorted(self.song_popularity.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'uptime': str(uptime).split('.')[0],
            'total_events': self.events_processed,
            'events_per_second': round(eps, 2),
            'unique_users': len(self.user_activity),
            'unique_songs_played': len(self.song_popularity),
            'top_users': top_users,
            'top_songs': top_songs,
            'action_distribution': dict(self.action_stats),
            'device_distribution': dict(self.device_stats),
            'location_distribution': dict(self.location_stats),
            'recent_events_count': len(recent_100)
        }
    
    def print_dashboard(self):
        """Print a real-time dashboard"""
        while self.running:
            try:
                # Clear screen (works on most terminals)
                print('\033[2J\033[H')
                
                metrics = self.calculate_metrics()
                
                print("🎵 MUSIC STREAMING ANALYTICS - REAL-TIME DASHBOARD")
                print("=" * 60)
                print(f"⏱️  Uptime: {metrics['uptime']}")
                print(f"📊 Total Events: {metrics['total_events']:,}")
                print(f"⚡ Events/sec: {metrics['events_per_second']}")
                print(f"👥 Unique Users: {metrics['unique_users']}")
                print(f"🎵 Unique Songs Played: {metrics['unique_songs_played']}")
                print()
                
                print("🔥 TOP ACTIVE USERS:")
                for user, count in metrics['top_users']:
                    print(f"   {user}: {count} events")
                print()
                
                print("🎯 TOP PLAYED SONGS:")
                for song, count in metrics['top_songs']:
                    print(f"   {song}: {count} plays")
                print()
                
                print("📱 DEVICE DISTRIBUTION:")
                total_device_events = sum(metrics['device_distribution'].values())
                for device, count in metrics['device_distribution'].items():
                    percentage = (count / total_device_events * 100) if total_device_events > 0 else 0
                    print(f"   {device}: {count} ({percentage:.1f}%)")
                print()
                
                print("🎭 ACTION DISTRIBUTION:")
                total_actions = sum(metrics['action_distribution'].values())
                for action, count in metrics['action_distribution'].items():
                    percentage = (count / total_actions * 100) if total_actions > 0 else 0
                    print(f"   {action}: {count} ({percentage:.1f}%)")
                print()
                
                print("🌍 TOP LOCATIONS:")
                top_locations = sorted(metrics['location_distribution'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]
                for location, count in top_locations:
                    print(f"   {location}: {count} events")
                print()
                
                print("🔄 RECENT ACTIVITY:")
                if self.recent_events:
                    latest_event = self.recent_events[-1]
                    print(f"   Last Event: {latest_event['user_id']} {latest_event['action']} {latest_event['song_id']}")
                    print(f"   Device: {latest_event['device']} | Location: {latest_event['location']}")
                
                print()
                print("Press Ctrl+C to stop monitoring...")
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"❌ Dashboard error: {e}")
                time.sleep(5)
    
    def monitor_stream(self):
        """Main monitoring loop"""
        print("🎵 Starting Music Streaming Monitor...")
        print("📡 Listening to topic: music.play_events")
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                event = message.value
                self.process_event(event)
                
                # Print progress every 100 events
                if self.events_processed % 100 == 0:
                    print(f"📈 Processed {self.events_processed} events...")
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitor...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown"""
        self.running = False
        self.consumer.close()
        print(f"✅ Monitor stopped. Total events processed: {self.events_processed}")
    
    def start(self, dashboard=True):
        """Start monitoring with optional dashboard"""
        if dashboard:
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=self.monitor_stream)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Run dashboard in main thread
            self.print_dashboard()
        else:
            # Just run monitoring
            self.monitor_stream()

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Received interrupt signal...')
    monitor_instance.running = False
    sys.exit(0)

if __name__ == "__main__":
    monitor_instance = StreamingMonitor()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Check command line arguments
    dashboard_mode = True
    if len(sys.argv) > 1 and sys.argv[1] == '--no-dashboard':
        dashboard_mode = False
        print("Running in simple monitoring mode (no dashboard)")
    
    # Start monitoring
    monitor_instance.start(dashboard=dashboard_mode)
