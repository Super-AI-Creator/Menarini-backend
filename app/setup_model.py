import openai, os
import json
from transformers import pipeline
from dotenv import load_dotenv
import requests

load_dotenv()

OPENAI_KEY = os.environ.get("OPENAI_KEY")
OPENAI_API_URL = os.environ.get("OPENAI_API_URL")
OPENAI_EMBEDDING_API_URL = os.environ.get("OPENAI_EMBEDDING_API_URL")
GEMENI_API_KEY = os.environ.get("GEMENI_API_KEY")
PROXIES = {
    "http": "socks5://14a3c03a0e246:5f2f6b72e4@168.158.126.246:12324",
    "https": "socks5://14a3c03a0e246:5f2f6b72e4@168.158.126.246:12324"
}

def create_prompt_from_text(text_data):
    # Define the fields to extract
    fields = ['Purchase Order Number (PO#)', 'Invoice Number', 'Item Code', 'Quantity', 'Batch Number', 'Document Date']
    
    # Construct the prompt with flexibility for various formats and languages
    prompt = (
        "You are a highly intelligent and multilingual assistant capable of understanding and extracting structured data "
        "from various formats of text, including different languages. I need you to identify and extract specific fields "
        "from the provided text. Please be aware that the fields might not be present, and the formats can vary. If a field "
        "is missing, simply return 'null' for that field. The fields I need are:\n"
        f"{', '.join(fields)}.\n\n"
        "Please return the extracted information as a JSON object. Here is the text:\n\n"
        f"{text_data}\n\n"
        "Ensure your response follows this JSON format exactly:\n"
        "[\n"
        "   {\n"
        "     \"Purchase Order Number (PO#)\": \"value or null\",\n"
        "     \"Invoice Number\": \"value or null\",\n"
        "     \"Item Code\": \"value or null\",\n"
        "     \"Quantity\": \"value or null\",\n"
        "     \"Batch Number\": \"value or null\",\n"
        "     \"Document Date\": \"value or null\"\n"
        "   }\n"
        "]\n"
        "Remember to consider context clues and language variations to accurately extract the fields."
    )
    return prompt


def setup_text_gen_model():
    """
    Setup models for GPT-4 text generation and classification.
    """
    try:
        # Function for GPT-4 text generation using OpenAI API
        def gpt4_text_generation(text_data, max_tokens=4096):
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_KEY}",
            }

            # Replace `create_prompt_from_text` with your logic for generating prompts
            prompt = text_data

            payload = {
                "model": "gpt-4",
                "messages": [
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
            }
            response = requests.post(
                OPENAI_API_URL, headers=headers, json=payload, proxies=PROXIES
            )
            
            if response.status_code == 200:
                response_content = response.json().get("choices")[0]["message"]["content"]
                # Extract the JSON part of the response
                json_start = response_content.find("[")
                json_end = response_content.rfind("]") + 1
                if json_start == -1 or json_end == -1:
                    raise ValueError("JSON content not found in the GPT-4 response")

                json_string = response_content[json_start:json_end]
                try:
                    extracted_fields = json.loads(json_string)
                    # Ensure it's a list as expected
                    return extracted_fields[0]
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to decode JSON content: {e}")

            else:
                raise Exception(
                    f"API request failed with status code {response.status_code}: {response.text}"
                )

        

        return gpt4_text_generation

    except Exception as e:
        raise RuntimeError(f"Model setup failed: {e}")
