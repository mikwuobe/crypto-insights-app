# File: backend/sentiment_analyzer.py
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import os
import time

# --- Configuration ---
# Path to the directory where your fine-tuned model was saved
MODEL_PATH = "./models/distilbert-finetuned-financial-sentiment"
# --------------------

# --- Load Local Model Pipeline (ONCE on startup) ---
print(f"Initializing sentiment analysis pipeline from local path: {MODEL_PATH}")
start_time = time.time()
sentiment_pipeline = None # Initialize as None

try:
    # Check if model path exists
    if not os.path.exists(MODEL_PATH):
         raise OSError(f"Model directory not found at: {MODEL_PATH}. Please ensure training completed successfully.")

    # Determine device (mps for Apple Silicon, cuda for Nvidia, else cpu)
    device_name = "cpu" # Default to CPU
    if torch.cuda.is_available():
        device_name = "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available(): # Check MPS availability correctly
         device_name = "mps"
    print(f"Attempting to load model on device: {device_name}")

    # Use device index if needed (0 for first GPU usually)
    device_index = 0 if device_name in ["cuda", "mps"] else -1

    # Load the pipeline using the local path
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model=MODEL_PATH,
        tokenizer=MODEL_PATH, # Load tokenizer from same path
        device=device_index # Use device index for pipeline
    )
    end_time = time.time()
    print(f"Local sentiment analysis pipeline loaded successfully in {end_time - start_time:.2f} seconds.")

    # Optional: Test pipeline output format
    try:
        test_output = sentiment_pipeline("This is only a test.")
        print(f"Pipeline test output format: {test_output}")
        # Expected: [{'label': 'neutral', 'score': 0.9...}] or similar (labels might be upper/lower case)
    except Exception as e:
        print(f"Could not perform pipeline test: {e}")

except Exception as e:
    print(f"ERROR: Failed to load local sentiment analysis pipeline from {MODEL_PATH}: {e}")
    print("Sentiment analysis will not be available.")
# --------------------------------------------------


def map_label_local(raw_label):
    """Maps local pipeline labels to standard upper-case labels."""
    # Local pipeline might output 'positive', 'negative', 'neutral' (lowercase)
    # We need POSITIVE, NEGATIVE, NEUTRAL to match the rest of the app
    label_upper = str(raw_label).upper()
    if label_upper == "POSITIVE": return "POSITIVE"
    if label_upper == "NEGATIVE": return "NEGATIVE"
    if label_upper == "NEUTRAL": return "NEUTRAL"
    print(f"Warning: Unknown sentiment label encountered from local pipeline: {raw_label}")
    return "NEUTRAL" # Default to neutral


def analyze_sentiment(text):
    """Analyzes sentiment of a single text string using the local pipeline."""
    if not sentiment_pipeline: return "UNKNOWN" # Pipeline failed to load
    if not text or not isinstance(text, str): return "NEUTRAL"

    try:
        # Local pipeline usually returns list of dicts, e.g. [{'label': 'neutral', 'score': 0.9...}]
        result = sentiment_pipeline(text)
        if result and isinstance(result, list) and result[0] and 'label' in result[0]:
            raw_label = result[0]['label']
            return map_label_local(raw_label)
        else:
            print(f"Warning: Unexpected result format from local pipeline for text: {text[:50]}...")
            return "UNKNOWN"
    except Exception as e:
        print(f"Error during local sentiment analysis for text '{text[:50]}...': {e}")
        return "UNKNOWN"


def analyze_sentiment_batch(texts):
    """Analyzes sentiment for a list of texts using the local pipeline (batch processing)."""
    if not sentiment_pipeline: return ["UNKNOWN"] * len(texts or [])
    if not texts or not isinstance(texts, list): return ["NEUTRAL"] * len(texts or [])

    # Filter out empty/invalid items before sending to pipeline
    valid_texts = [str(t) for t in texts if t and isinstance(t, str)]
    if not valid_texts: return ["NEUTRAL"] * len(texts) # Return neutral for original invalid items

    results_map = {}
    try:
        # Pipeline handles batching internally
        results = sentiment_pipeline(valid_texts)
        # Expected format: [{'label': 'positive', 'score': ...}, {'label': 'negative', ...}]
        if results and isinstance(results, list) and len(results) == len(valid_texts):
            for i, result_dict in enumerate(results):
                if result_dict and 'label' in result_dict:
                    raw_label = result_dict['label']
                    results_map[valid_texts[i]] = map_label_local(raw_label)
                else:
                    print(f"Warning: Unexpected item format in batch response for '{valid_texts[i][:50]}...': {result_dict}")
                    results_map[valid_texts[i]] = "UNKNOWN"
        else:
            print(f"Warning: Unexpected local pipeline response format or length mismatch for batch: {results}")
            for text in valid_texts: results_map[text] = "UNKNOWN"

    except Exception as e:
        print(f"Error during local batch sentiment analysis: {e}")
        for text in valid_texts: results_map[text] = "UNKNOWN"

    # Reconstruct the final list matching the original input 'texts' order
    final_sentiments = [results_map.get(str(t), "NEUTRAL") for t in texts]
    return final_sentiments

# --- Example Usage (Optional) ---
if __name__ == '__main__':
    print("\nTesting Sentiment Analyzer with LOCAL model...")
    if sentiment_pipeline:
        test_headline = "Bitcoin price surges!"
        sentiment = analyze_sentiment(test_headline)
        print(f"'{test_headline}' -> Sentiment: {sentiment}")

        headlines = ["Ethereum upgrade successful.", "Market crashes.", "Stablecoin okay.", "", None]
        sentiments = analyze_sentiment_batch(headlines)
        for h, s in zip(headlines, sentiments):
             print(f"'{h}' -> Sentiment: {s}")
    else:
        print("Skipping direct execution tests as local pipeline failed to load.")