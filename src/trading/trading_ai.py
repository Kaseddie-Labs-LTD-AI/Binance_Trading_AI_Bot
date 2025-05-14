import os
from google.cloud import aiplatform
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
GOOGLE_CLOUD_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GOOGLE_PROJECT_ID = os.getenv("GOOGLE_PROJECT_ID")
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION")
GOOGLE_ENDPOINT_ID = os.getenv("GOOGLE_ENDPOINT_ID")

# Validate that required environment variables exist
if not GOOGLE_CLOUD_CREDENTIALS or not GOOGLE_PROJECT_ID or not GOOGLE_LOCATION or not GOOGLE_ENDPOINT_ID:
    raise ValueError("❌ Missing required environment variables. Check your .env file!")

# Set the environment variable for Google Cloud authentication
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CLOUD_CREDENTIALS

def get_market_insights(query):
    """Fetch AI-driven market insights from Google Vertex AI."""
    try:
        client = aiplatform.gapic.PredictionServiceClient()

        response = client.predict(
            endpoint=f"projects/{GOOGLE_PROJECT_ID}/locations/{GOOGLE_LOCATION}/endpoints/{GOOGLE_ENDPOINT_ID}",
            instances=[{"query": query}],
            parameters={},
        )

        # Extract AI-generated insight from response
        predictions = response.predictions if response.predictions else []
        ai_output = predictions[0].get("insight", "⚠️ No AI insights available.") if predictions else "⚠️ No insights received."
        return ai_output

    except Exception as e:
        return f"❌ AI request failed: {str(e)}"

# Example test
if __name__ == "__main__":
    test_query = "Current trend for BTCUSDT"
    print(get_market_insights(test_query))