# File: backend/app.py
import os
from flask import Flask, jsonify, request # Keep request import
from flask_cors import CORS
from dotenv import load_dotenv
import time
from datetime import datetime
from flask_caching import Cache # Keep Cache import

# --- Local Imports ---
from news_fetcher import fetch_all_crypto_news # Ensure this is updated later
from sentiment_analyzer import analyze_sentiment
# from sentiment_analyzer import analyze_sentiment_batch

# --- Load Environment Variables ---
load_dotenv()

# --- Initialize Flask App ---
app = Flask(__name__)

# --- Cache Configuration (Keep existing) ---
cache_config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(cache_config)
cache = Cache(app)
# -------------------------

# --- CORS Configuration (Keep existing) ---
default_origins = "http://localhost:5173"
allowed_origins_str = os.getenv('ALLOWED_ORIGINS', default_origins)
allowed_origins_list = [origin.strip() for origin in allowed_origins_str.split(',')]
print(f"Configuring CORS for origins: {allowed_origins_list}")
CORS(app, resources={r"/api/*": {"origins": allowed_origins_list}})
# -------------------------

# --- Helper Function (Keep existing) ---
def calculate_overall_sentiment(articles):
    # ... (implementation) ...
    if not articles: return "NEUTRAL", "UNKNOWN"
    positive_count = sum(1 for a in articles if a.get('sentiment') == 'POSITIVE')
    negative_count = sum(1 for a in articles if a.get('sentiment') == 'NEGATIVE')
    neutral_count = sum(1 for a in articles if a.get('sentiment') == 'NEUTRAL')
    total_analyzed = positive_count + negative_count + neutral_count
    if total_analyzed == 0: return "NEUTRAL", "UNKNOWN"
    sentiment_score = (positive_count - negative_count) / total_analyzed
    overall_sentiment = "NEUTRAL"
    if sentiment_score > 0.15: overall_sentiment = "POSITIVE"
    elif sentiment_score < -0.15: overall_sentiment = "NEGATIVE"
    trend = "Neutral"
    if overall_sentiment == "POSITIVE": trend = "Bullish"
    elif overall_sentiment == "NEGATIVE": trend = "Bearish"
    print(f"Sentiment counts: POS={positive_count}, NEG={negative_count}, NEU={neutral_count}")
    print(f"Overall sentiment: {overall_sentiment}, Trend: {trend} (Score: {sentiment_score:.2f})")
    return overall_sentiment, trend
# -------------------------

# --- API Endpoint ---
@app.route('/api/crypto-data', methods=['GET'])
@cache.cached(timeout=300, query_string=True) # Keep caching decorator
def get_crypto_data():
    start_process_time = time.time()
    print("\nExecuting get_crypto_data function (Cache Miss or First Request)")

    # --- Get Date Query Parameters --- << MODIFIED >>
    from_date_str = request.args.get('from', None) # e.g., '2025-04-01'
    to_date_str = request.args.get('to', None)     # e.g., '2025-04-05'
    print(f"Received query params - From: {from_date_str}, To: {to_date_str}")
    # ----------------------------------

    # --- Fetch News (passing dates) --- << MODIFIED >>
    # Pass dates; hours_ago=None tells fetcher to use dates if available
    news_articles = fetch_all_crypto_news(hours_ago=None, from_date=from_date_str, to_date=to_date_str)
    # ----------------------------------

    # --- Perform Sentiment Analysis (Keep existing options) ---
    print(f"Analyzing sentiment for {len(news_articles)} articles...")
    analysis_start_time = time.time()
    for article in news_articles:
         article['sentiment'] = analyze_sentiment(article.get('title', ''))
    analysis_duration = time.time() - analysis_start_time
    print(f"Sentiment analysis took {analysis_duration:.2f} seconds.")
    # ---------------------------------

    # --- Calculate Overall Stats (Keep existing) ---
    overall_sentiment, trend = calculate_overall_sentiment(news_articles)
    # -----------------------------

    end_process_time = time.time()
    print(f"Total processing time (cache miss): {end_process_time - start_process_time:.2f} seconds.")

    # --- Return JSON Response (Keep existing) ---
    return jsonify({
        "message": f"Processed {len(news_articles)} unique articles.",
        "timestamp": datetime.utcnow().isoformat() + 'Z',
        "news": news_articles,
        "overall_sentiment": overall_sentiment,
        "trend": trend
    })
# -------------------------

# --- Run the App (Keep existing) ---
if __name__ == '__main__':
    app.run()
# -------------------------