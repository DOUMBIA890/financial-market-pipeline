with source as (

    select *
    from {{ source('raw', 'crypto_prices') }}

),

cleaned as (

    select
        crypto,
        price_usd,
        "timestamp",
        date("timestamp") as date_only,
        cast(price_usd as numeric) as price_usd_clean

    from source

),

deduplicated as (

    select
        *,
        row_number() over (
            partition by crypto, price_usd, date("timestamp")
            order by "timestamp" desc
        ) as rn

    from cleaned

)

select
    crypto,
    price_usd,
    price_usd_clean,
    "timestamp",
    date_only

from deduplicated
where rn = 1