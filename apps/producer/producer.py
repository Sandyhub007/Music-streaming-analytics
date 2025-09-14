from kafka import KafkaProducer
import json, time, uuid, random
from datetime import datetime, timedelta
from faker import Faker
import threading
import signal
import sys

fake = Faker()

# Enhanced data for more realistic simulation
USERS = [f"user_{i}" for i in range(1, 101)]  # 100 users
SONGS = [
    {"id": f"song_{i}", "title": fake.catch_phrase(), "duration": random.randint(120, 300)} 
    for i in range(1, 501)  # 500 songs with metadata
]
ARTISTS = [f"artist_{i}" for i in range(1, 51)]  # 50 artists
ACTIONS = ["play", "pause", "skip", "complete"]
DEVICES = ["mobile", "web", "tv", "desktop"]
LOCATIONS = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", 
             "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville"]

class MusicStreamingProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            max_block_ms=5000
        )
        self.running = True
        self.events_produced = 0
        self.user_sessions = {}  # Track user sessions for realistic behavior
        
    def generate_realistic_event(self):
        """Generate more realistic music streaming events"""
        user_id = random.choice(USERS)
        
        # Get or create user session
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "current_song": None,
                "session_start": datetime.utcnow(),
                "device": random.choice(DEVICES),
                "location": random.choice(LOCATIONS),
                "listening_history": []
            }
        
        session = self.user_sessions[user_id]
        
        # Determine action based on current state
        if session["current_song"] is None:
            # Start new song
            action = "play"
            song = random.choice(SONGS)
            session["current_song"] = song
        else:
            # Choose action based on realistic probabilities
            action_weights = {
                "pause": 0.15,
                "skip": 0.20,
                "complete": 0.05,
                "play": 0.60  # Continue playing
            }
            action = random.choices(list(action_weights.keys()), 
                                  weights=list(action_weights.values()))[0]
            song = session["current_song"]
            
            if action in ["skip", "complete"]:
                # End current song, next event will start new one
                session["current_song"] = None
                session["listening_history"].append(song["id"])
        
        # Add some session cleanup (reset after 2 hours of inactivity)
        if datetime.utcnow() - session["session_start"] > timedelta(hours=2):
            self.user_sessions[user_id] = {
                "current_song": None,
                "session_start": datetime.utcnow(),
                "device": random.choice(DEVICES),
                "location": random.choice(LOCATIONS),
                "listening_history": []
            }
            session = self.user_sessions[user_id]
        
        # Create event
        event = {
            "event_id": str(uuid.uuid4()),
            "event_ts": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "song_id": song["id"] if song else random.choice(SONGS)["id"],
            "artist_id": random.choice(ARTISTS),
            "action": action,
            "device": session["device"],
            "location": session["location"],
            "song_duration": song.get("duration", 180) if song else 180,
            "session_id": f"session_{hash(user_id + str(session['session_start']))}"
        }
        
        return event
    
    def produce_events(self):
        """Main event production loop"""
        print("🎵 Starting Music Streaming Producer...")
        print(f"📊 Simulating {len(USERS)} users, {len(SONGS)} songs, {len(ARTISTS)} artists")
        
        try:
            while self.running:
                event = self.generate_realistic_event()
                
                try:
                    self.producer.send("music.play_events", event)
                    self.events_produced += 1
                    
                    if self.events_produced % 10 == 0:
                        print(f"📈 Produced {self.events_produced} events")
                    
                    if self.events_produced % 100 == 0:
                        print(f"👥 Active sessions: {len(self.user_sessions)}")
                    
                    # Variable sleep time for more realistic event distribution
                    sleep_time = random.uniform(0.1, 2.0)
                    time.sleep(sleep_time)
                    
                except Exception as e:
                    print(f"❌ Error producing event: {e}")
                    time.sleep(5)
                    
        except KeyboardInterrupt:
            print("\n🛑 Stopping producer...")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown"""
        self.running = False
        self.producer.flush()
        self.producer.close()
        print(f"✅ Producer stopped. Total events produced: {self.events_produced}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n🛑 Received interrupt signal...')
    producer_instance.running = False

if __name__ == "__main__":
    producer_instance = MusicStreamingProducer()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start producing events
    producer_instance.produce_events()
