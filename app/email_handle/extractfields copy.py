import requests
import json
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_parse import LlamaParse
from app.config.env import OPENAI_KEY, OPENAI_API_URL, PROXIES, LLAMA_API_KEY, OPENAI_API_KEY


def load_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        text_data = f.read()
    return text_data

def load_positions_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    return ocr_data
def create_prompt_from_text(parsed_text):
    fields = ['PO#','DN#','Item Code' ,  'Quantity', 'Batch#', 'Document Date', 'Incoterms', 'Date of loading', ' Executed on', 'Batch#', 'Manufacturing Date', 'Expiry Date', 'Best Before Date', 'Date of receipt','Posting Date',  'Packing Slip#', 'Supplier' 'INV NO#']
    doc_type = ['Delivery Note (DN)','Packing List (PL)', 'Invoice - Commercial(INV)', 'Financial Invoice(INV)', 'Bill of Lading', 'Air Waybill', 'Certificate of Analysis(COA)',]
    # Construct the prompt with flexibility for various formats and languages
    prompt = (
        "You are a highly intelligent and multilingual assistant capable of understanding and extracting structured data from various formats of text, including different languages."
        "I wil give you the document as the text."
        "I need you to classify the document, identify and extract specific fields from document."
        "Please be aware that the fields might not be present, and the formats can vary. "
        "If a field is missing, simply return 'null' for that field."
        "Fields are :\n"
        f"{', '.join(fields)}.\n\n"
        "These are document type.\n"
        f"{', '.join(doc_type)}.\n\n"
        "This is document\n"
        f"{', '.join(parsed_text)}.\n\n"
        "According to the document type, you have to identify different fields."
        "These are the fields for each document type.\n\n"

        "The Quantity must be integer.\n\n"
        
        "Delivery Note (DN) or Packing List (PL) => DN#, PO#, Item Code, Document Date, Quantity, Manufacturing Date, Batch#, Packing Slip#, Supplier, Expiry Date, Incoterms\n\n"

        "Invoice - Commercial or Financial Invoice => PO#,Item Code, Packing Slip#,  Incoterms, Quantity, Batch#, Posting Date, Manufacturing Date, INV NO#, Expiry Date, Document Date\n\n"

        "Bill of Lading  =>Incoterms, Posting Date\n\n"

        "Air Waybill => Incoterms, Posting Date\n\n"

        "Certificate of Analysis (COA) => Manufacturing Date, Expiry Date\n\n"

        "Please return the extracted information as a JSON object."
        "Ensure your response follows this JSON format exactly."
        "The Doc Type must be short word, like DN, PL and so on, except Bill of Lading, Air Waybill and Cargo Checklist"
        "Please send me data as like this."
        "[\n"
                "   {\n"
                "     \"Doc Type\": \"DN\",\n"
                "     \"PO\": \"1345245\",\n"
                "     \"Supplier Item Code\": \"439275\",\n"
                "   }\n"
        "]\n"
    )
    return prompt

def extract_fields_using_gpt(text_data, prompt_type):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}",
    }
    # if prompt_type == 0:
    #     prompt = text_data
    # else:
    #     prompt = create_prompt_from_text(text_data)
    
    # payload = {
    #     "model": "gpt-4o",
    #     "messages": [
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         },
    #     ],
    #     "max_tokens": 4096,  # Adjust this if needed
    #     "temperature": 0.1
    # }

    # response = requests.post(OPENAI_API_URL, headers=headers, json=payload, proxies=PROXIES)
    
    if prompt_type == 0:
        prompt = text_data
    else:
        prompt = create_prompt_from_text(text_data)
    llama_parse = LlamaParse(
        api_key=LLAMA_API_KEY,
        language="en",
        result_type="markdown",
        parsing_instruction=prompt,
    )
    print("----------------------------------")
    print(llama_parse)
    # Load data with LlamaParse
    documents = llama_parse.load_data(text_data)
    print("Generated Documents for Llama:", json.dumps(documents, indent=2))
    try:
        json_data = json.dumps(documents)  # Try converting to JSON string
        documents = json.loads(json_data)  # Parse back into JSON object
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON structure in documents: {e}")

    # Send the data to OpenAI API
    response = requests.post(OPENAI_API_URL, headers=headers, json=documents, proxies=PROXIES)
    
    print("-----------------------------------------------------------------------------------")
    print(response)
    if response.status_code == 200:
        response_content = response.json().get("choices")[0]["message"]["content"]
        print("Response content:", response_content)  # Debugging: Print the content received

        # Extract the JSON part of the response
        json_start = response_content.find("[")
        json_end = response_content.rfind("]") + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("JSON content not found in the GPT-4o response")
        
        json_string = response_content[json_start:json_end]

        try:
            extracted_fields = json.loads(json_string)
            # Ensure it's a list as expected
            if isinstance(extracted_fields, list) and len(extracted_fields) > 0:
                return extracted_fields  # Return the first object in the list
            else:
                raise ValueError("Unexpected format in extracted fields JSON")
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON content: {e}")

    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

def extract_field(txt_path, output_path):
    text_data = load_text_from_txt(txt_path)
    
    extracted_fields = extract_fields_using_gpt(text_data, 1)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_fields, f, ensure_ascii=False, indent=4)

    print(f"Extracted fields with positions saved to {output_path}")
    
    return extracted_fields
def get_basic_data(text_data):
    basic_detail = extract_fields_using_gpt(text_data, 0)
    return basic_detail