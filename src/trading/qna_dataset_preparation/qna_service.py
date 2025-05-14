# qna_service.py
# Refined Python code for querying Vertex AI Search and using a Gemini LLM

# Ensure you have installed the necessary Google Cloud client libraries:
# pip install google-cloud-aiplatform google-cloud-discoveryengine vertexai

from google.cloud import discoveryengine_v1alpha as discoveryengine
import vertexai # Import the Vertex AI SDK
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig # For Gemini

import json
import os

# --- Configuration ---
PROJECT_ID_STRING = "binance-trading-ai-bot" 
PROJECT_NUMBER_FOR_DISCOVERY_ENGINE = "598618882640" 

LOCATION = "us"  # Location of your Search App/Engine
ENGINE_ID = "kaseddie-rag_1746872692740" # YOUR APP/ENGINE ID
SERVING_CONFIG_ID = "default_search" # Usually "default_search" or "default_config" for an App

# For Gemini models via Vertex AI
VERTEX_AI_LOCATION = "us-central1" 
GEMINI_MODEL_NAME = "gemini-2.0-flash-001" # UPDATED: Using Gemini 2.0 Flash

# --- Initialize Clients ---

def init_discovery_engine_client():
    """Initializes the Discovery Engine (Vertex AI Search) client."""
    try:
        api_endpoint = "discoveryengine.googleapis.com" if LOCATION == "global" else f"{LOCATION}-discoveryengine.googleapis.com"
        
        client_options = {"api_endpoint": api_endpoint}
        client = discoveryengine.SearchServiceClient(client_options=client_options)
        print(f"Discovery Engine client initialized successfully for endpoint: {api_endpoint}")
        return client
    except Exception as e:
        print(f"Error initializing Discovery Engine client: {e}")
        raise 

def init_vertex_ai():
    """Initializes the Vertex AI SDK."""
    try:
        vertexai.init(project=PROJECT_ID_STRING, location=VERTEX_AI_LOCATION)
        print(f"Vertex AI SDK initialized successfully for project '{PROJECT_ID_STRING}' in location '{VERTEX_AI_LOCATION}'.")
    except Exception as e:
        print(f"Error initializing Vertex AI SDK: {e}")
        raise

# --- Function to Search Your Datastore via an App/Engine ---
def search_app_engine(client, user_query: str, engine_id: str = ENGINE_ID):
    """Queries your Vertex AI Search App/Engine."""
    if not client:
        print("Discovery Engine client is not initialized.")
        return []

    serving_config_str = (
        f"projects/{PROJECT_NUMBER_FOR_DISCOVERY_ENGINE}/locations/{LOCATION}/"
        f"collections/default_collection/engines/{engine_id}/servingConfigs/{SERVING_CONFIG_ID}"
    )
    print(f"Attempting to search with App/Engine serving_config: {serving_config_str}")

    request = discoveryengine.SearchRequest(
        serving_config=serving_config_str,
        query=user_query,
        page_size=3,
        content_search_spec=discoveryengine.SearchRequest.ContentSearchSpec(
            snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
                return_snippet=True,
                max_snippet_count=1 
            ),
            extractive_content_spec=discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
                 max_extractive_answer_count=1, 
                 max_extractive_segment_count=1 
            )
        )
    )
    
    retrieved_chunks = []
    try:
        search_response = client.search(request)
        print("\n--- Retrieved Chunks from Datastore: ---")
        if not search_response.results:
            print("  No results returned from the datastore search.")

        for result_idx, result in enumerate(search_response.results):
            document_data = result.document
            content_snippet = ""
            source_id = document_data.id if document_data.id else document_data.name 

            print(f"Processing result {result_idx + 1} (ID: {source_id})")

            # Attempt 1: From derived_struct_data (extractive_answers, snippets, extractive_segments)
            if document_data.derived_struct_data:
                for key_attempt in ['extractive_answers', 'snippets', 'extractive_segments']:
                    data_list = document_data.derived_struct_data.get(key_attempt)
                    if data_list and len(data_list) > 0:
                        item_info_map_composite = data_list[0] 
                        
                        # print(f"    DEBUG: Attempting to extract from derived_struct_data.{key_attempt}[0]")
                        # if hasattr(item_info_map_composite, 'items'):
                        #      print(f"      DEBUG: Keys in item_info_map_composite: {list(item_info_map_composite.keys())}")
                        #      for k, v in item_info_map_composite.items():
                        #          print(f"        DEBUG: item_info_map_composite['{k}'] (type: {type(v)}): {str(v)[:100]}...")

                        if key_attempt == 'snippets':
                            if 'snippet' in item_info_map_composite:
                                content_snippet = item_info_map_composite['snippet']
                        else: 
                            if 'content' in item_info_map_composite:
                                content_snippet = item_info_map_composite['content']
                        
                        if content_snippet and isinstance(content_snippet, str): 
                            print(f"  Extracted from derived_struct_data.{key_attempt}")
                            break 
                        else: 
                            content_snippet = "" 
            
            # Attempt 2: Fallback to Document.Content.text
            if not content_snippet and hasattr(document_data, 'content') and document_data.content and hasattr(document_data.content, 'text') and document_data.content.text:
                content_snippet = "".join(list(document_data.content.text)) 
                if content_snippet:
                    print(f"  Extracted from document_data.content.text")
            
            if content_snippet:
                print(f"  Source Document Path: {document_data.name}") 
                print(f"  Retrieved Snippet/Content: {content_snippet[:500]}...") 
                retrieved_chunks.append(content_snippet)
            else:
                print(f"  No direct content/snippet found in expected fields for document {source_id}.")
                print(f"    DEBUG: document_data.derived_struct_data ALL ITEMS: {dict(document_data.derived_struct_data.items()) if document_data.derived_struct_data else 'None'}")


    except Exception as e:
        print(f"Error during datastore search: {e}")
    
    print("--------------------------------------")
    return retrieved_chunks

# --- Function to Generate Answer with LLM (Using Vertex AI Gemini SDK) ---
def generate_answer_with_llm(user_query: str, context_chunks: list):
    """Generates an answer using a Gemini model with provided context."""
    
    context_str = "\n\n".join(context_chunks)
    
    prompt = f"""You are a helpful AI assistant for a cryptocurrency application.
Answer the following user's question based *only* on the provided context from our knowledge base.
If the context doesn't contain enough information to answer the question accurately, clearly state that you don't have enough information from the provided documents.
Do not make up answers or use external knowledge.

User Question:
{user_query}

Context from Knowledge Base:
---
{context_str}
---

Answer:
"""
    print("\n--- Prompt to LLM: ---")
    print(prompt[:1000] + "..." if len(prompt) > 1000 else prompt) 
    print("----------------------")

    try:
        model = GenerativeModel(GEMINI_MODEL_NAME)
        
        generation_config = GenerationConfig(
            temperature=0.2,      
            top_p=0.8,
            top_k=40,
            max_output_tokens=512 
        )
        
        response = model.generate_content(
            [prompt], 
            generation_config=generation_config,
        )
        
        answer = response.text 
        print("\n--- LLM Answer: ---")
        print(answer)
        print("--------------------")
        return answer
        
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "I encountered an issue trying to generate an answer. Please try again."

# --- Main Q&A Function ---
def ask_ai_qna(user_query: str):
    """Handles the end-to-end Q&A process."""
    try:
        init_vertex_ai() 
        discovery_client = init_discovery_engine_client()
        
        retrieved_context = search_app_engine(discovery_client, user_query) 
        
        if not retrieved_context:
            print("No relevant information found in the datastore for your query.")
            return "I couldn't find specific information on that topic in my current knowledge base."
            
        llm_answer = generate_answer_with_llm(user_query, retrieved_context)
        return llm_answer
    except Exception as e:
        print(f"An error occurred in the Q&A process: {e}")
        return "Sorry, I encountered an error while processing your request."

# --- Example Usage ---
if __name__ == "__main__":
    # Ensure your environment is authenticated with Google Cloud
    # and APIs are enabled.

    query1 = "What is Bitcoin?"
    print(f"\n\n>>> Asking: {query1}")
    answer1 = ask_ai_qna(query1)
    print(f"\n>>> Final Answer for '{query1}':\n{answer1}")

    query2 = "How do I use stop-loss orders in your app?"
    print(f"\n\n>>> Asking: {query2}")
    answer2 = ask_ai_qna(query2)
    print(f"\n>>> Final Answer for '{query2}':\n{answer2}")
    
    query3 = "What is the current price of Ethereum?" 
    print(f"\n\n>>> Asking: {query3}")
    answer3 = ask_ai_qna(query3)
    print(f"\n>>> Final Answer for '{query3}':\n{answer3}")

