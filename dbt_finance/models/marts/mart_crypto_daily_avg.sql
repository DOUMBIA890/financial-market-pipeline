with base as (

    select *
    from {{ ref('stg_crypto_prices') }}

)

select
    crypto,
    date_only,
    avg(price_usd) as avg_price_usd,
    min(price_usd) as min_price_usd,
    max(price_usd) as max_price_usd,
    count(*) as nb_observations

from base
group by crypto, date_only