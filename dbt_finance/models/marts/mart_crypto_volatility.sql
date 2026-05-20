with base as (

    select *
    from {{ ref('stg_crypto_prices') }}

),

daily as (

    select
        crypto,
        date_only,
        max(price_usd) as max_price,
        min(price_usd) as min_price,
        (max(price_usd) - min(price_usd)) as volatility
    from base
    group by crypto, date_only

)

select *
from daily