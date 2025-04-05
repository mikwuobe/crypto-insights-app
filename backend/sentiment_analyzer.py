from transformers import pipeline
import time 

print("Initializing sentiment analysis pipeline...")
start_time = time.time()


try:
    
    sentiment_pipeline = pipeline(
        "sentiment-analysis",
        model="finiteautomata/bertweet-base-sentiment-analysis",
        device=-1 
    )
    end_time = time.time()
    print(f"Sentiment analysis pipeline loaded successfully in {end_time - start_time:.2f} seconds.")

    
    try:
        test_output = sentiment_pipeline("This is a test sentence.")
        print(f"Pipeline test output format: {test_output}")
       
    except Exception as e:
        print(f"Could not perform pipeline test: {e}")

except Exception as e:
    print(f"ERROR: Failed to load sentiment analysis pipeline: {e}")
    print("Sentiment analysis will not be available.")
    
    sentiment_pipeline = None


def analyze_sentiment(text):
    """
    Analyzes the sentiment of a given text using the pre-loaded pipeline.

    Args:
        text (str): The text (e.g., news headline) to analyze.

    Returns:
        str: The sentiment label ('POSITIVE', 'NEGATIVE', 'NEUTRAL')
             or 'UNKNOWN' if analysis fails or the pipeline isn't loaded.
    """
    if not sentiment_pipeline:
        return "UNKNOWN" 

    
    if not text or not isinstance(text, str):
        return "NEUTRAL" 

    try:
       
        result = sentiment_pipeline(text)

        if result and isinstance(result, list) and 'label' in result[0]:
            raw_label = result[0]['label']
          
            if raw_label == "POS":
                return "POSITIVE"
            elif raw_label == "NEG":
                return "NEGATIVE"
            elif raw_label == "NEU":
                return "NEUTRAL"
            else:
                print(f"Warning: Unknown sentiment label encountered: {raw_label}")
                return "NEUTRAL" 
        else:
            print(f"Warning: Unexpected result format from pipeline for text: {text[:50]}...")
            return "UNKNOWN"

    except Exception as e:
        print(f"Error during sentiment analysis for text '{text[:50]}...': {e}")
        return "UNKNOWN" 


def analyze_sentiment_batch(texts):
    """
    Analyzes sentiment for a list of texts using batch processing (more efficient).

    Args:
        texts (list): A list of strings (e.g., news headlines) to analyze.

    Returns:
        list: A list of sentiment labels ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNKNOWN').
              The order corresponds to the input list. Returns empty list on major errors.
    """
    if not sentiment_pipeline or not texts:
        return ["UNKNOWN"] * len(texts or [])

    results_labels = []
    try:
        
        results = sentiment_pipeline(texts)

        for result in results:
             if result and isinstance(result, dict) and 'label' in result:
                 raw_label = result['label']
                 if raw_label == "POS":
                     results_labels.append("POSITIVE")
                 elif raw_label == "NEG":
                     results_labels.append("NEGATIVE")
                 elif raw_label == "NEU":
                     results_labels.append("NEUTRAL")
                 else:
                     print(f"Warning: Unknown sentiment label encountered in batch: {raw_label}")
                     results_labels.append("NEUTRAL")
             else:
                 print(f"Warning: Unexpected result format from pipeline in batch.")
                 results_labels.append("UNKNOWN")

    except Exception as e:
        print(f"Error during batch sentiment analysis: {e}")
        
        return ["UNKNOWN"] * len(texts)

    return results_labels

if __name__ == '__main__':
    if sentiment_pipeline:
        print("\nTesting analyze_sentiment:")
        test_headline = "Bitcoin price surges above $70,000!"
        sentiment = analyze_sentiment(test_headline)
        print(f"'{test_headline}' -> Sentiment: {sentiment}")

        test_headline_neg = "Crypto market crashes after regulatory concerns."
        sentiment_neg = analyze_sentiment(test_headline_neg)
        print(f"'{test_headline_neg}' -> Sentiment: {sentiment_neg}")

        print("\nTesting analyze_sentiment_batch:")
        headlines = [
            "Ethereum upgrade successful, gas fees drop.",
            "New NFT project rug pulls investors.",
            "Stablecoin reserves remain fully backed.",
            "", 
            None 
        ]
        sentiments = analyze_sentiment_batch(headlines)
        for h, s in zip(headlines, sentiments):
            print(f"'{h}' -> Sentiment: {s}")
    else:
        print("Skipping direct execution tests as pipeline failed to load.")