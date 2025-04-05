import requests
import os
import time

MODEL_NAME = "finiteautomata/bertweet-base-sentiment-analysis"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    print("WARNING: Hugging Face API Token (HF_API_TOKEN) not found in environment variables. Sentiment analysis will fail.")
# --------------------

HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

def query_hf_api(payload):
    """Sends data to the Hugging Face Inference API and handles response/errors."""
    if not HF_API_TOKEN:
        return None 

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20) 

        if response.status_code == 429:
            print("Hugging Face API rate limit hit. Try again later.")
            return None
        if response.status_code == 503:
            
            wait_time = response.headers.get("Retry-After")
            print(f"Model potentially loading, retrying after {wait_time or 5} sec...")
            time.sleep(float(wait_time or 5))
            response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=20)
            print(f"Retry status: {response.status_code}")

        response.raise_for_status() 
        # ----------------------------------------------

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"Error querying Hugging Face API: {e}")
        return None
    except Exception as e:
         print(f"An unexpected error occurred during HF API query: {e}")
         return None

def map_label(raw_label):
    """Maps HF API labels ('POS', 'NEG', 'NEU') to standard labels."""
    if raw_label == "POS": return "POSITIVE"
    if raw_label == "NEG": return "NEGATIVE"
    if raw_label == "NEU": return "NEUTRAL"
    print(f"Warning: Unknown sentiment label encountered from API: {raw_label}")
    return "NEUTRAL" 


def analyze_sentiment(text):
    """Analyzes sentiment of a single text string using HF Inference API."""
    if not text or not isinstance(text, str):
        return "NEUTRAL" 

    payload = {"inputs": text}
    api_response = query_hf_api(payload)

    try:
        if api_response and isinstance(api_response, list) and api_response[0] and isinstance(api_response[0], list) and api_response[0][0]:
            raw_label = api_response[0][0].get('label')
            return map_label(raw_label)
        else:
             print(f"Warning: Unexpected API response format for single text '{text[:50]}...': {api_response}")
             return "UNKNOWN"
    except (IndexError, KeyError, TypeError) as e:
        print(f"Error parsing single API response for '{text[:50]}...': {e}, Response: {api_response}")
        return "UNKNOWN"


def analyze_sentiment_batch(texts):
    """Analyzes sentiment for a list of texts using HF Inference API."""
    if not texts or not isinstance(texts, list):
        return ["NEUTRAL"] * len(texts or [])

    valid_texts = [str(t) for t in texts if t and isinstance(t, str)]
    if not valid_texts:
         
         return ["NEUTRAL"] * len(texts)

    payload = {"inputs": valid_texts}
    api_response = query_hf_api(payload)
    results_map = {} 

    try:
        if api_response and isinstance(api_response, list) and len(api_response) == len(valid_texts):
            for i, result_list in enumerate(api_response):
                if result_list and isinstance(result_list, list) and result_list[0]:
                     raw_label = result_list[0].get('label')
                     results_map[valid_texts[i]] = map_label(raw_label) 
                else:
                    print(f"Warning: Unexpected item format in batch response for '{valid_texts[i][:50]}...': {result_list}")
                    results_map[valid_texts[i]] = "UNKNOWN"
        else:
            print(f"Warning: Unexpected API response format or length mismatch for batch: {api_response}")
            
            for text in valid_texts: results_map[text] = "UNKNOWN"

    except (IndexError, KeyError, TypeError) as e:
        print(f"Error parsing batch API response: {e}, Response: {api_response}")
        for text in valid_texts: results_map[text] = "UNKNOWN"

    final_sentiments = [results_map.get(str(t), "NEUTRAL") for t in texts] 
    return final_sentiments

if __name__ == '__main__':
    print("Testing Sentiment Analyzer with Hugging Face API...")
    
    if not HF_API_TOKEN:
         print("Please set the HF_API_TOKEN environment variable for testing.")
    else:
        test_headline = "Bitcoin price surges!"
        sentiment = analyze_sentiment(test_headline)
        print(f"'{test_headline}' -> Sentiment: {sentiment}")

        headlines = ["Ethereum upgrade successful.", "Market crashes.", "Stablecoin okay.", "", None]
        sentiments = analyze_sentiment_batch(headlines)
        for h, s in zip(headlines, sentiments):
             print(f"'{h}' -> Sentiment: {s}")