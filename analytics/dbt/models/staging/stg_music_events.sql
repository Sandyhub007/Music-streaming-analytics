-- Staging model for raw music streaming events
{{ config(materialized='view') }}

with source_data as (
    select
        event_id,
        event_ts,
        user_id,
        song_id,
        artist_id,
        action,
        device,
        location,
        -- Add derived fields
        extract(hour from event_ts) as event_hour,
        extract(dow from event_ts) as day_of_week,
        date_trunc('day', event_ts) as event_date,
        case 
            when action = 'play' then 1
            else 0
        end as is_play_event,
        case 
            when action = 'skip' then 1
            else 0
        end as is_skip_event,
        case 
            when action = 'complete' then 1
            else 0
        end as is_complete_event
    from {{ source('raw', 'music_events') }}
    where event_ts is not null
      and user_id is not null
      and song_id is not null
)

select * from source_data
