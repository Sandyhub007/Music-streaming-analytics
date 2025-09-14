-- Hourly platform usage and engagement analytics
{{ config(materialized='table') }}

with hourly_stats as (
    select
        event_date,
        event_hour,
        device,
        location,
        count(*) as total_events,
        count(distinct user_id) as unique_users,
        count(distinct song_id) as unique_songs,
        count(distinct artist_id) as unique_artists,
        sum(is_play_event) as total_plays,
        sum(is_skip_event) as total_skips,
        sum(is_complete_event) as total_completes,
        avg(case when is_play_event = 1 then 1.0 else 0.0 end) as play_rate
    from {{ ref('stg_music_events') }}
    group by event_date, event_hour, device, location
),

hourly_metrics as (
    select
        event_date,
        event_hour,
        device,
        location,
        total_events,
        unique_users,
        unique_songs,
        unique_artists,
        total_plays,
        total_skips,
        total_completes,
        play_rate,
        -- Calculate average events per user
        (total_events::float / nullif(unique_users, 0))::numeric(5,2) as avg_events_per_user,
        -- Peak hour indicator
        case 
            when event_hour between 6 and 9 then 'Morning Rush'
            when event_hour between 12 and 14 then 'Lunch Break'
            when event_hour between 17 and 20 then 'Evening Peak'
            when event_hour between 21 and 23 then 'Night Hours'
            else 'Off Peak'
        end as time_period,
        -- Device performance
        case 
            when device = 'mobile' and total_events > 10 then 'Mobile Heavy'
            when device = 'web' and total_events > 10 then 'Web Heavy'
            when device = 'tv' and total_events > 10 then 'TV Heavy'
            else 'Standard'
        end as device_usage_pattern
    from hourly_stats
)

select * from hourly_metrics
