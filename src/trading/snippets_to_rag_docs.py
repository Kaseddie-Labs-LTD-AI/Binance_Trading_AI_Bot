# snippets_to_rag_docs.py
import json
import os

# Define the input JSON file (created by your Intial_Knowledge.py script)
# and the output directory for the RAG documents.
snippets_file_name = 'knowledge_base_snippets.json'
input_directory = 'qna_dataset_preparation' # This is where knowledge_base_snippets.json should be
rag_docs_output_dir = os.path.join(input_directory, 'rag_documents/') # Subdirectory for RAG docs

# Construct the full path to the snippets file
snippets_file_path = os.path.join(input_directory, snippets_file_name)

# Ensure the output directory exists
os.makedirs(rag_docs_output_dir, exist_ok=True)

try:
    # Open and load the knowledge snippets from the JSON file
    with open(snippets_file_path, 'r', encoding='utf-8') as f:
        knowledge_snippets = json.load(f)

    if not knowledge_snippets:
        print(f"No snippets found in '{snippets_file_path}'. Please ensure 'knowledge_base_snippets.json' exists in the '{input_directory}' folder and contains data.")
    else:
        print(f"Found {len(knowledge_snippets)} snippets in '{snippets_file_path}'. Converting to RAG documents...")
        
        successful_conversions = 0
        for i, snippet in enumerate(knowledge_snippets):
            # Get the necessary fields from the snippet
            topic_id = snippet.get("topic_id", f"untitled_snippet_{i+1}") # Default if topic_id is missing
            title = snippet.get("title", "No Title")
            content = snippet.get("content", "")
            keywords_list = snippet.get("keywords", [])
            keywords_str = ", ".join(keywords_list) if keywords_list else "N/A"

            # Sanitize topic_id to create a valid filename (replace non-alphanumeric with underscore)
            filename_safe_topic_id = "".join(c if c.isalnum() else "_" for c in topic_id)
            doc_filename = f"{filename_safe_topic_id}.txt" # Save as .txt files
            doc_filepath = os.path.join(rag_docs_output_dir, doc_filename)

            # Write the content to the new text file
            try:
                with open(doc_filepath, 'w', encoding='utf-8') as doc_file:
                    doc_file.write(f"Title: {title}\n")
                    doc_file.write(f"Keywords: {keywords_str}\n\n") # Adding keywords can sometimes help retrieval
                    doc_file.write(content)
                
                print(f"Created RAG document: {doc_filepath}")
                successful_conversions += 1
            except Exception as e_write:
                print(f"Error writing file {doc_filepath}: {e_write}")
        
        print(f"\nSuccessfully converted {successful_conversions} of {len(knowledge_snippets)} snippets to documents in '{rag_docs_output_dir}'.")
        if successful_conversions > 0:
            print("These documents can now be uploaded to Google Cloud Storage and indexed using Vertex AI Search or Vector Search for your RAG system.")
        else:
            print("No documents were converted. Please check for errors or empty snippet data.")

except FileNotFoundError:
    print(f"Error: The file '{snippets_file_path}' was not found. Please ensure it exists and you ran your 'Intial_Knowledge.py' (or equivalent) script first.")
except json.JSONDecodeError:
    print(f"Error: The file '{snippets_file_path}' is not a valid JSON file. Please check its content.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
