import requests
import os

from datetime import datetime, timedelta, time, timezone

from dateutil import parser

NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"
CRYPTO_PANIC_BASE_URL = "https://cryptopanic.com/api/v1/posts/"
DEFAULT_HOURS_AGO = 24

def get_api_key(key_name):
    """Safely retrieves an API key from environment variables."""
    api_key = os.getenv(key_name)
    if not api_key:
        print(f"WARNING: API key '{key_name}' not found in .env file. This source will be skipped.")
    return api_key

def standardize_article(title, source, url, published_at_str, image_url=None):
    """Ensures essential fields are present and converts published_at to ISO 8601 string."""
    if not all([title, source, url, published_at_str]):
        return None
    try:
        published_dt = parser.parse(published_at_str)
        
        if published_dt.tzinfo is None or published_dt.tzinfo.utcoffset(published_dt) is None:
             published_dt = published_dt.replace(tzinfo=timezone.utc) # Assign UTC if naive
        else:
             published_dt = published_dt.astimezone(timezone.utc) # Convert existing TZ to UTC
        published_iso = published_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    except (ValueError, OverflowError, TypeError) as e:
        print(f"Skipping article due to invalid date format: {published_at_str}, Error: {e}")
        return None
    return {
        'title': title.strip() if title else "No Title",
        'source': source.strip() if source else "Unknown Source",
        'url': url,
        'published_at': published_iso, 
        'image_url': image_url
    }

def fetch_crypto_news_newsapi(hours_ago=DEFAULT_HOURS_AGO, from_date_str=None, to_date_str=None):
    """Fetches cryptocurrency news from NewsAPI.org, using date range if provided."""
    print("Attempting to fetch from NewsAPI.org...")
    api_key = get_api_key("NEWSAPI_ORG_KEY")
    if not api_key: return []
    params = {
        'q': '(crypto OR cryptocurrency OR bitcoin OR ethereum OR blockchain OR NFT OR web3) NOT (giveaway OR airdrop OR free)',
        'apiKey': api_key,'language': 'en','sortBy': 'publishedAt','pageSize': 50,
    }
    if from_date_str and to_date_str:
        params['from'] = from_date_str; params['to'] = to_date_str
        print(f"NewsAPI using date range: {from_date_str} to {to_date_str}")
    elif from_date_str:
        params['from'] = from_date_str
        print(f"NewsAPI using start date: {from_date_str}")
    elif hours_ago is not None:
        from_time_dt = datetime.now(timezone.utc) - timedelta(hours=hours_ago) 
        params['from'] = from_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"NewsAPI using hours ago: {hours_ago} (from {params['from']})")
    else:
        from_time_dt = datetime.now(timezone.utc) - timedelta(hours=DEFAULT_HOURS_AGO) 
        params['from'] = from_time_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"NewsAPI defaulting to last {DEFAULT_HOURS_AGO} hours.")

    articles_list = []
    try:
        response = requests.get(NEWSAPI_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        articles_raw = data.get('articles', [])
        for article in articles_raw:
            source_info = article.get('source', {})
            standardized = standardize_article(
                title=article.get('title'), source=source_info.get('name'),
                url=article.get('url'), published_at_str=article.get('publishedAt'),
                image_url=article.get('urlToImage')
            )
            if standardized: articles_list.append(standardized)
    except requests.exceptions.RequestException as e: print(f"Error fetching news from NewsAPI: {e}")
    except Exception as e: print(f"An unexpected error during NewsAPI fetching: {e}")
    print(f"Fetched {len(articles_list)} articles from NewsAPI.")
    return articles_list

def fetch_crypto_news_cryptopanic():
    """Fetches recent cryptocurrency news from CryptoPanic API."""
    print("Attempting to fetch from CryptoPanic...")
    api_key = get_api_key("CRYPTO_PANIC_KEY")
    if not api_key: return []
    params = {'auth_token': api_key, 'public': 'true'}
    articles_list = []
    try:
        response = requests.get(CRYPTO_PANIC_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        articles_raw = data.get('results', [])
        for article in articles_raw:
            standardized = standardize_article(
                title=article.get('title'), source=article.get('source', {}).get('domain'),
                url=article.get('url'), published_at_str=article.get('created_at'),
                image_url=None
            )
            if standardized: articles_list.append(standardized)
    except requests.exceptions.RequestException as e: print(f"Error fetching news from CryptoPanic: {e}")
    except Exception as e: print(f"An unexpected error during CryptoPanic fetching: {e}")
    print(f"Fetched {len(articles_list)} articles from CryptoPanic.")
    return articles_list

def fetch_all_crypto_news(hours_ago=DEFAULT_HOURS_AGO, from_date=None, to_date=None):
    """ Fetches news, passing dates to supported APIs and filtering others manually. """
    print(f"\nFetching all news - Dates: {from_date} to {to_date}, Fallback Hours: {hours_ago}")

    newsapi_articles = fetch_crypto_news_newsapi(hours_ago=hours_ago, from_date_str=from_date, to_date_str=to_date)
    cryptopanic_articles = fetch_crypto_news_cryptopanic()

    all_raw_articles = newsapi_articles + cryptopanic_articles

    filtered_by_date_articles = []
    start_dt = None
    end_dt = None

    if from_date:
         try:
             
             start_dt = datetime.strptime(from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc) 
         except ValueError: print(f"Invalid from_date format: {from_date}")
    if to_date:
         try:
             
             end_dt = datetime.combine(
                 datetime.strptime(to_date, '%Y-%m-%d'),
                 time.max 
             ).replace(tzinfo=timezone.utc) 
         except ValueError: print(f"Invalid to_date format: {to_date}")

    if start_dt or end_dt:
         print(f"Applying post-fetch date filter: Start={start_dt}, End={end_dt}")
         for article in all_raw_articles:
             try:
                 
                 article_dt = parser.parse(article['published_at']) 

                 
                 date_match = True
                 if start_dt and article_dt < start_dt: date_match = False
                 if end_dt and article_dt > end_dt: date_match = False

                 if date_match:
                      filtered_by_date_articles.append(article)

             except (ValueError, OverflowError, TypeError) as e:
                 print(f"Skipping article during date filter due to parse error: {article.get('published_at')}, {e}")
         print(f"Articles after post-fetch date filtering: {len(filtered_by_date_articles)}")
    else:
         
         filtered_by_date_articles = all_raw_articles

    
    print(f"\nTotal articles before de-duplication: {len(filtered_by_date_articles)}")
    unique_articles = {}
    for article in filtered_by_date_articles:
         url = article.get('url')
         if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
              if url not in unique_articles or (article.get('image_url') and not unique_articles[url].get('image_url')):
                  unique_articles[url] = article
         else: print(f"Skipping article due to missing/invalid URL: {article.get('title')}")
    deduplicated_list = list(unique_articles.values())
    print(f"Total articles after de-duplication: {len(deduplicated_list)}")

    
    try:
        sorted_articles = sorted(deduplicated_list, key=lambda x: x['published_at'], reverse=True)
    except Exception as e: print(f"Error sorting articles: {e}"); sorted_articles = deduplicated_list
    print(f"Final sorted article count: {len(sorted_articles)}")
    return sorted_articles

if __name__ == '__main__':
    print("Testing fetch_all_crypto_news...")
    from dotenv import load_dotenv
    load_dotenv()
    final_articles = fetch_all_crypto_news(hours_ago=48)
    if final_articles:
        print(f"\nSuccessfully fetched and processed {len(final_articles)} unique articles. First few:")
        for i, article in enumerate(final_articles[:5]):
             print(f"{i+1}. {article['title']} ({article['source']}) - {article['published_at']} - Img: {'Yes' if article.get('image_url') else 'No'}")
    else:
        print("\nCould not fetch articles from any source or an error occurred.")