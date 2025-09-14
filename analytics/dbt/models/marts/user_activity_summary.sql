-- User activity summary mart
{{ config(materialized='table') }}

with user_daily_activity as (
    select
        user_id,
        event_date,
        count(*) as total_events,
        count(distinct song_id) as unique_songs_played,
        count(distinct artist_id) as unique_artists_played,
        sum(is_play_event) as total_plays,
        sum(is_skip_event) as total_skips,
        sum(is_complete_event) as total_completes,
        -- Calculate listening session duration in minutes
        (extract(epoch from max(event_ts) - min(event_ts)) / 60)::numeric(10,2) as session_duration_minutes,
        array_agg(distinct device) as devices_used,
        array_agg(distinct location) as locations_visited
    from {{ ref('stg_music_events') }}
    group by user_id, event_date
),

user_metrics as (
    select
        user_id,
        event_date,
        total_events,
        unique_songs_played,
        unique_artists_played,
        total_plays,
        total_skips,
        total_completes,
        session_duration_minutes,
        devices_used,
        locations_visited,
        -- Calculate engagement metrics
        case 
            when total_plays > 0 then (total_completes::float / total_plays * 100)::numeric(5,2)
            else 0
        end as completion_rate_pct,
        case 
            when total_plays > 0 then (total_skips::float / total_plays * 100)::numeric(5,2)
            else 0
        end as skip_rate_pct,
        -- Categorize user activity level
        case 
            when total_events >= 50 then 'High'
            when total_events >= 20 then 'Medium'
            when total_events >= 5 then 'Low'
            else 'Minimal'
        end as activity_level
    from user_daily_activity
)

select * from user_metrics
