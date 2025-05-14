import google.generativeai as genai
import os

# Set your Gemini API key directly in the code (Make sure it's valid!)
API_KEY = "AIzaSyAVN_9HvulVnUJkwu-6DAjkok39iZR51lI"  # Replace with actual key
os.environ["GOOGLE_API_KEY"] = API_KEY

# Debug: Print API key to verify it’s being recognized
print("🔍 API Key in Code:", os.environ["GOOGLE_API_KEY"])  # Debugging

# Ensure API key is correctly set before proceeding
if not os.getenv("GOOGLE_API_KEY"):
    raise ValueError("❌ ERROR: Google API key not found. Please check your environment variables.")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Function to list available AI models
def list_available_models():
    try:
        print("\n📌 Checking Available AI Models...")
        models = genai.list_models()
        print("\n✅ Available Models for Your API Key:")
        for model in models:
            print(f"- {model.name}")
    except Exception as e:
        print("\n❌ ERROR: Unable to list models.")
        print("📌 Possible Fixes:")
        print("- Ensure your API key is valid.")
        print("- Check your Google Cloud API permissions.")

# Function to generate an AI-powered trading strategy
def generate_trading_strategy():
    try:
        print("\n🚀 Requesting AI-generated trading strategy...")

        # Use the correct model name from the available models list
        model = genai.GenerativeModel("gemini-2.5-pro-preview-03-25")  # Replaced incorrect model name

        response = model.generate_content("Write a trading strategy for Bitcoin.")

        print("\n🔥 AI-Generated Trading Strategy:\n")
        print(response.text if hasattr(response, 'text') else "⚠️ No response text available.")

    except Exception as e:
        print("\n❌ ERROR:", e)
        print("📌 Possible Fixes:")
        print("- Verify your API key in Google Cloud Console.")
        print("- Ensure you have access to Gemini models in Vertex AI.")
        print("- Run `pip install --upgrade google-generativeai` to update.")

# Main Execution
if __name__ == "__main__":
    list_available_models()  # First, list available models
    generate_trading_strategy()  # Then, try generating a strategy