#!/usr/bin/env python3
"""
Music Streaming Analytics - Web Dashboard
Real-time web UI for monitoring music streaming analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import time
from collections import defaultdict, deque
from kafka import KafkaConsumer
import threading
from datetime import datetime, timedelta
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="🎵 Music Streaming Analytics",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'metrics' not in st.session_state:
    st.session_state.metrics = {
        'total_events': 0,
        'unique_users': set(),
        'unique_songs': set(),
        'user_activity': defaultdict(int),
        'song_popularity': defaultdict(int),
        'device_stats': defaultdict(int),
        'action_stats': defaultdict(int),
        'location_stats': defaultdict(int),
        'recent_events': deque(maxlen=100),
        'hourly_events': defaultdict(int),
        'start_time': datetime.now()
    }

def create_kafka_consumer():
    """Create Kafka consumer for real-time data"""
    try:
        consumer = KafkaConsumer(
            "music.play_events",
            bootstrap_servers="localhost:9092",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="latest",
            enable_auto_commit=True,
            group_id="dashboard-consumer",
            consumer_timeout_ms=1000
        )
        return consumer
    except Exception as e:
        st.error(f"Failed to connect to Kafka: {e}")
        return None

def process_kafka_events():
    """Process Kafka events and update metrics"""
    consumer = create_kafka_consumer()
    if not consumer:
        return
    
    try:
        for message in consumer:
            event = message.value
            
            # Update metrics
            st.session_state.metrics['total_events'] += 1
            st.session_state.metrics['unique_users'].add(event['user_id'])
            st.session_state.metrics['unique_songs'].add(event['song_id'])
            st.session_state.metrics['user_activity'][event['user_id']] += 1
            st.session_state.metrics['action_stats'][event['action']] += 1
            st.session_state.metrics['device_stats'][event['device']] += 1
            st.session_state.metrics['location_stats'][event['location']] += 1
            st.session_state.metrics['recent_events'].append(event)
            
            if event['action'] == 'play':
                st.session_state.metrics['song_popularity'][event['song_id']] += 1
            
            # Time-based metrics
            event_time = datetime.fromisoformat(event['event_ts'])
            hour_key = event_time.strftime('%H:00')
            st.session_state.metrics['hourly_events'][hour_key] += 1
            
    except Exception as e:
        st.error(f"Error processing events: {e}")
    finally:
        if consumer:
            consumer.close()

def create_metrics_overview():
    """Create metrics overview cards"""
    metrics = st.session_state.metrics
    uptime = datetime.now() - metrics['start_time']
    eps = metrics['total_events'] / uptime.total_seconds() if uptime.total_seconds() > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Events",
            value=f"{metrics['total_events']:,}",
            delta=f"+{len(metrics['recent_events'])} recent"
        )
    
    with col2:
        st.metric(
            label="👥 Unique Users",
            value=len(metrics['unique_users']),
            delta=f"{eps:.2f} events/sec"
        )
    
    with col3:
        st.metric(
            label="🎵 Unique Songs",
            value=len(metrics['unique_songs']),
            delta=f"⏱️ {str(uptime).split('.')[0]} uptime"
        )
    
    with col4:
        most_active = max(metrics['user_activity'].items(), key=lambda x: x[1]) if metrics['user_activity'] else ("", 0)
        st.metric(
            label="🔥 Most Active User",
            value=most_active[0],
            delta=f"{most_active[1]} events"
        )

def create_action_distribution_chart():
    """Create action distribution pie chart"""
    if not st.session_state.metrics['action_stats']:
        return None
    
    actions = list(st.session_state.metrics['action_stats'].keys())
    counts = list(st.session_state.metrics['action_stats'].values())
    
    fig = px.pie(
        values=counts,
        names=actions,
        title="🎭 Action Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_device_distribution_chart():
    """Create device distribution bar chart"""
    if not st.session_state.metrics['device_stats']:
        return None
    
    devices = list(st.session_state.metrics['device_stats'].keys())
    counts = list(st.session_state.metrics['device_stats'].values())
    
    fig = px.bar(
        x=devices,
        y=counts,
        title="📱 Device Usage Distribution",
        color=devices,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_layout(showlegend=False)
    return fig

def create_top_songs_chart():
    """Create top songs chart"""
    if not st.session_state.metrics['song_popularity']:
        return None
    
    top_songs = dict(sorted(st.session_state.metrics['song_popularity'].items(), 
                           key=lambda x: x[1], reverse=True)[:10])
    
    if not top_songs:
        return None
    
    songs = list(top_songs.keys())
    plays = list(top_songs.values())
    
    fig = px.bar(
        x=plays,
        y=songs,
        orientation='h',
        title="🎯 Top 10 Most Played Songs",
        color=plays,
        color_continuous_scale="viridis"
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def create_location_map():
    """Create geographic distribution chart"""
    if not st.session_state.metrics['location_stats']:
        return None
    
    locations = list(st.session_state.metrics['location_stats'].keys())
    counts = list(st.session_state.metrics['location_stats'].values())
    
    fig = px.bar(
        x=locations,
        y=counts,
        title="🌍 Geographic Distribution",
        color=counts,
        color_continuous_scale="blues"
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def create_hourly_activity_chart():
    """Create hourly activity chart"""
    if not st.session_state.metrics['hourly_events']:
        return None
    
    hours = sorted(st.session_state.metrics['hourly_events'].keys())
    counts = [st.session_state.metrics['hourly_events'][h] for h in hours]
    
    fig = px.line(
        x=hours,
        y=counts,
        title="⏰ Hourly Activity Pattern",
        markers=True
    )
    fig.update_traces(line_color='#ff6b6b', line_width=3)
    return fig

def create_recent_events_table():
    """Create recent events table"""
    if not st.session_state.metrics['recent_events']:
        return None
    
    recent = list(st.session_state.metrics['recent_events'])[-10:]  # Last 10 events
    
    df = pd.DataFrame([
        {
            'Time': event['event_ts'][-8:],  # Just show time
            'User': event['user_id'],
            'Action': event['action'],
            'Song': event['song_id'],
            'Device': event['device'],
            'Location': event['location']
        }
        for event in reversed(recent)
    ])
    
    return df

# Main Dashboard
def main():
    st.title("🎵 Music Streaming Analytics Dashboard")
    st.markdown("Real-time monitoring of music streaming events")
    
    # Sidebar controls
    st.sidebar.title("📊 Dashboard Controls")
    auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh", value=True)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 10, 5)
    
    if st.sidebar.button("🔄 Manual Refresh") or auto_refresh:
        # Process new events
        process_kafka_events()
    
    # Metrics Overview
    st.header("📈 Key Metrics")
    create_metrics_overview()
    
    # Charts Section
    st.header("📊 Analytics Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Action Distribution
        action_chart = create_action_distribution_chart()
        if action_chart:
            st.plotly_chart(action_chart, use_container_width=True)
        
        # Device Distribution
        device_chart = create_device_distribution_chart()
        if device_chart:
            st.plotly_chart(device_chart, use_container_width=True)
    
    with col2:
        # Top Songs
        songs_chart = create_top_songs_chart()
        if songs_chart:
            st.plotly_chart(songs_chart, use_container_width=True)
        
        # Hourly Activity
        hourly_chart = create_hourly_activity_chart()
        if hourly_chart:
            st.plotly_chart(hourly_chart, use_container_width=True)
    
    # Geographic Distribution
    st.header("🌍 Geographic Analysis")
    location_chart = create_location_map()
    if location_chart:
        st.plotly_chart(location_chart, use_container_width=True)
    
    # Recent Events
    st.header("🔄 Recent Activity")
    recent_df = create_recent_events_table()
    if recent_df is not None and not recent_df.empty:
        st.dataframe(recent_df, use_container_width=True)
    else:
        st.info("No recent events to display. Make sure the Kafka producer is running.")
    
    # Status Information
    with st.expander("ℹ️ System Status"):
        st.json({
            "Kafka Topic": "music.play_events",
            "Consumer Group": "dashboard-consumer",
            "Auto Refresh": auto_refresh,
            "Refresh Interval": f"{refresh_interval}s",
            "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Auto refresh
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    main()
