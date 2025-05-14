from google.cloud import aiplatform

# Initialize Vertex AI
aiplatform.init(project="your_project_id", location="us-central1")

# Create generative AI model instance
model = aiplatform.GenerativeModel(model_name="gemini-2.0-pro")

# Test AI response
response = model.generate_content("Write a trading strategy for Bitcoin.")
print(response.text)