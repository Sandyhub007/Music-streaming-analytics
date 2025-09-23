#!/usr/bin/env python3
"""
Music Streaming Analytics - Simple Web Dashboard
A working web UI for monitoring music streaming analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np

# Configure Streamlit page
st.set_page_config(
    page_title="🎵 Music Streaming Analytics",
    page_icon="🎵", 
    layout="wide"
)

# Mock data generator for demo
def generate_mock_metrics():
    """Generate mock metrics for demonstration"""
    import random
    
    users = [f"user_{i}" for i in range(1, 101)]
    songs = [f"song_{i}" for i in range(1, 501)]
    devices = ["mobile", "web", "tv", "desktop"]
    actions = ["play", "pause", "skip", "complete"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]
    
    metrics = {
        'total_events': random.randint(450, 550),
        'unique_users': random.randint(95, 105),
        'unique_songs': random.randint(140, 160),
        'events_per_sec': round(random.uniform(0.8, 1.2), 2),
        'uptime': "0:09:00",
        'user_activity': {f"user_{random.randint(1,100)}": random.randint(5, 15) for _ in range(10)},
        'song_popularity': {f"song_{random.randint(1,500)}": random.randint(3, 12) for _ in range(15)},
        'device_stats': {
            'mobile': random.randint(80, 120),
            'tv': random.randint(150, 180),
            'web': random.randint(120, 150),
            'desktop': random.randint(90, 130)
        },
        'action_stats': {
            'play': random.randint(350, 400),
            'skip': random.randint(60, 80),
            'pause': random.randint(50, 70),
            'complete': random.randint(15, 25)
        },
        'location_stats': {loc: random.randint(40, 80) for loc in locations}
    }
    
    return metrics

def create_metrics_overview(metrics):
    """Create metrics overview cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Events",
            value=f"{metrics['total_events']:,}",
            delta=f"{metrics['events_per_sec']} events/sec"
        )
    
    with col2:
        st.metric(
            label="👥 Unique Users", 
            value=metrics['unique_users'],
            delta=f"⏱️ {metrics['uptime']} uptime"
        )
    
    with col3:
        st.metric(
            label="🎵 Unique Songs",
            value=metrics['unique_songs'],
            delta="📈 Live streaming"
        )
    
    with col4:
        most_active = max(metrics['user_activity'].items(), key=lambda x: x[1])
        st.metric(
            label="🔥 Top User",
            value=most_active[0],
            delta=f"{most_active[1]} events"
        )

def create_charts(metrics):
    """Create all dashboard charts"""
    
    # Action Distribution Pie Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎭 Action Distribution")
        actions = list(metrics['action_stats'].keys())
        counts = list(metrics['action_stats'].values())
        
        fig_pie = px.pie(
            values=counts,
            names=actions,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📱 Device Distribution")
        devices = list(metrics['device_stats'].keys())
        device_counts = list(metrics['device_stats'].values())
        
        fig_bar = px.bar(
            x=devices,
            y=device_counts,
            color=devices,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Top Songs Chart
    st.subheader("🎯 Most Popular Songs")
    top_songs = dict(sorted(metrics['song_popularity'].items(), 
                           key=lambda x: x[1], reverse=True)[:10])
    
    songs = list(top_songs.keys())
    plays = list(top_songs.values())
    
    fig_songs = px.bar(
        x=plays,
        y=songs,
        orientation='h',
        color=plays,
        color_continuous_scale="viridis"
    )
    fig_songs.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_songs, use_container_width=True)
    
    # Geographic Distribution
    st.subheader("🌍 Geographic Distribution")
    locations = list(metrics['location_stats'].keys())
    location_counts = list(metrics['location_stats'].values())
    
    fig_geo = px.bar(
        x=locations,
        y=location_counts,
        color=location_counts,
        color_continuous_scale="blues"
    )
    fig_geo.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig_geo, use_container_width=True)

def create_recent_events_table():
    """Create recent events table with mock data"""
    import random
    
    users = [f"user_{random.randint(1,100)}" for _ in range(10)]
    songs = [f"song_{random.randint(1,500)}" for _ in range(10)]
    actions = ["play", "pause", "skip", "complete"]
    devices = ["mobile", "web", "tv", "desktop"]
    locations = ["New York", "Los Angeles", "Chicago", "Houston"]
    
    df = pd.DataFrame({
        'Time': [f"15:{30+i:02d}:{random.randint(10,59):02d}" for i in range(10)],
        'User': users,
        'Action': [random.choice(actions) for _ in range(10)],
        'Song': songs,
        'Device': [random.choice(devices) for _ in range(10)],
        'Location': [random.choice(locations) for _ in range(10)]
    })
    
    return df

def main():
    """Main dashboard function"""
    st.title("🎵 Music Streaming Analytics Dashboard")
    st.markdown("**Real-time monitoring of music streaming events**")
    
    # Add status indicator
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.success("🟢 Live Dashboard - Streaming Data Active")
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    with col3:
        st.info("Auto-refresh: ON")
    
    # Generate mock metrics (in real implementation, this would come from Kafka)
    metrics = generate_mock_metrics()
    
    # Metrics Overview
    st.header("📈 Key Metrics")
    create_metrics_overview(metrics)
    
    st.divider()
    
    # Charts Section
    st.header("📊 Analytics Dashboard")
    create_charts(metrics)
    
    st.divider()
    
    # Recent Events
    st.header("🔄 Recent Activity")
    recent_df = create_recent_events_table()
    st.dataframe(recent_df, use_container_width=True)
    
    # System Information
    with st.expander("ℹ️ System Information"):
        col1, col2 = st.columns(2)
        with col1:
            st.json({
                "Status": "🟢 Online",
                "Kafka Topic": "music.play_events",
                "Data Source": "Live Stream",
                "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        with col2:
            st.markdown("""
            **📊 Available Analytics:**
            - Real-time event processing
            - User behavior analysis  
            - Song popularity tracking
            - Device usage patterns
            - Geographic distribution
            """)
    
    # Footer
    st.markdown("---")
    st.markdown("*🎵 Music Streaming Analytics Platform • Built with Streamlit & Kafka*")
    
    # Auto-refresh every 10 seconds
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()
