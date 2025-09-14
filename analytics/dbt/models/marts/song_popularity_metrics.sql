-- Song popularity and performance metrics
{{ config(materialized='table') }}

with song_daily_stats as (
    select
        song_id,
        artist_id,
        event_date,
        count(*) as total_events,
        sum(is_play_event) as total_plays,
        sum(is_skip_event) as total_skips,
        sum(is_complete_event) as total_completes,
        count(distinct user_id) as unique_listeners,
        count(distinct location) as unique_locations,
        count(distinct device) as unique_devices
    from {{ ref('stg_music_events') }}
    group by song_id, artist_id, event_date
),

song_metrics as (
    select
        song_id,
        artist_id,
        event_date,
        total_events,
        total_plays,
        total_skips,
        total_completes,
        unique_listeners,
        unique_locations,
        unique_devices,
        -- Performance metrics
        case 
            when total_plays > 0 then (total_completes::float / total_plays * 100)::numeric(5,2)
            else 0
        end as completion_rate_pct,
        case 
            when total_plays > 0 then (total_skips::float / total_plays * 100)::numeric(5,2)
            else 0
        end as skip_rate_pct,
        -- Engagement score (weighted combination of metrics)
        (
            (total_plays * 1.0) + 
            (total_completes * 2.0) + 
            (unique_listeners * 1.5) - 
            (total_skips * 0.5)
        )::numeric(10,2) as engagement_score,
        -- Popularity tier
        case 
            when total_plays >= 100 then 'Viral'
            when total_plays >= 50 then 'Popular'
            when total_plays >= 20 then 'Trending'
            when total_plays >= 5 then 'Emerging'
            else 'New'
        end as popularity_tier
    from song_daily_stats
)

select * from song_metrics
