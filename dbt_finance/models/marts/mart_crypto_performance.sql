with base as (

    select *
    from {{ ref('stg_crypto_prices') }}

),

ordered as (

    select
        crypto,
        date_only,
        price_usd,
        lag(price_usd) over (
            partition by crypto
            order by date_only
        ) as prev_price

    from base

),

performance as (

    select
        crypto,
        date_only,
        price_usd,
        prev_price,
        case 
            when prev_price is null then null
            else ((price_usd - prev_price) / prev_price) * 100
        end as pct_change

    from ordered

)

select *
from performance