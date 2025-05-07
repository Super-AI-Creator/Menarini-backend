import requests
import json
from app.config.env import OPENAI_KEY, OPENAI_API_URL, PROXIES
from app.email_handle.database_handler import get_supplier_list 
def load_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        text_data = f.read()
    return text_data

def load_positions_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)
    return ocr_data

def create_prompt_from_text(parsed_text):
    supplier_list = [supplier[0] for supplier in get_supplier_list()]
    # print(supplier_list)
    # Construct the prompt with flexibility for various formats and languages
    # prompt=(
    #     "Please analyze this document."
    #     "I wil give you the document as the text."
    #     "The document is one of Delivery Note (DELIVERY NOTE), Despatch Note(DESPATCH NOTE), Packing List (PACKING  LIST), Invoice(INVOICE), Bill of Lading(BILL OF LADING), Air Waybill(AIR WAYBILL) and Certificate of Analysis(CIRTIFICATE OF ANALYSIS)\n"
    #     "Let's express the document type as short word.\n"
    #     "Delivery Note / Despatch Note => DN\n"
    #     "Packing List => PL\n"
    #     "Invoice => INV\n"
    #     "Certificate of Analysis => COA\n"
    #     "Bill of Lading => Bill of Lading\n"
    #     "Air Waybill => Air Waybill\n"
    #     "This is document\n"
    #     f"{', '.join(parsed_text)}.\n\n"
    #     "Please find these fields in the document according to the document type."
    #     "DN or PL => DN#, Supplier,  PO#\n\n"
    #     "INV => PO#, DN#, Supplier , Supplier,INV NO#\n\n"
    #     "Bill of Lading  => Supplier \n\n"
    #     "Air Waybill =>  Supplier \n\n"
    #     "COA =>  Supplier \n\n"
        
    #     "Here, DN# is same as PL#, so return PL# as DN#."
    #     "The Supplier can be after `Deliver to` in DN. One after `Sold to` is not Supplier in INV. The Supplier can be after `Supplied by` in INV.   But before give me , analyze the meaning. For example, if the result you got is `BRANCH OF ZUELLIG PHARMA VIETNAM LT`, the exact Supplier is `ZUELLIG PHARMA VIETNAM LT`.\n\n"
    #     "The Packing List is same as Delivery Note. So if the document type is PL return the Doc Type as DN and also PL# as DN#."
        
    #     "Sometimes the document contains several types of doc like DN or PL, INV and so on as it's part. For instance, from page 1 to page 3 is INV , from page 3 to page 5 is PL or DN and From page 5 to 7 is BOL"
    #     "In that case, find the all doc type and as the type of each doc, return several times. Don't skip any doc type. But don't analysis one page for several times. I mean that after you get the doc type from analysis, don't analyze those anymore."
    #     "The Payment doc is unnecessary.Skip it. Safety Data Sheet doc is also unnecessary, Skip it."
    #     "We need only Invoice, Delivery Note, Packing List, Air Waybill and Bill of Lading."
    #     "And on the top of each page, there is document type."
    #     "Don't conflict the one type document and multi type document."
    #     "If the document is multi type document, there must be at least 3 Doc Type - DN & INV & COA or PL & INV & COA. If the document contains only 2, that is not multi-type document."
    #     "Don't miss any field for each doc."
    #     "Please return the extracted information as a JSON object."
    #     "Ensure your response follows this JSON format exactly."
    #     "The Doc Type must be short word, like DN, PL and COA. Not Delivery Note, Packing List or Certificate of Analysis.  But Bill of Lading and Air Waybill must not be short words."
    #     "Please send me data as like this form."
    #     "[\n"
    #             "   {\n"
    #             "     \"Doc Type\": \"DN\",\n"
    #             "     \"PO#\": \"1345245\",\n"
    #             "     \"DN#\": \"1345245\",\n"
    #             "   }\n"
    #     "]\n"
    # )


    prompt = (
            "You are an expert document parser.\n\n"

            "Your task is to analyze the following OCR'd document (text form) and extract structured information from it.\n\n"

            "The document may contain multiple document types. Valid types are:\n"
            "- Delivery Note or Despatch Note → **DN**\n"
            "- Packing List → **PL** (Treat exactly like DN)\n"
            "- Invoice → **INV**\n"
            "- Certificate of Analysis → **COA**\n"
            "- Bill of Lading → **Bill of Lading**\n"
            "- Air Waybill → **Air Waybill**\n\n"

            "**DO NOT include any other document types** like Payment Instructions or Safety Data Sheet (SDS). Skip those completely.\n\n"

            "**Critical Rules:**\n"
            "1. Analyze the document **page by page** — each page has its document type on top.\n"
            "2. **Do not analyze the same page more than once. Do NOT reanalyze the same part more than once.**\n"
            "3. **Packing List (PL)** must be treated as **Delivery Note (DN)**.\n"
            "   - Convert 'PL#' to `DN#`\n"
            "   - Set `Doc Type` as `DN`\n"
            "4. If the document contains at least 2 doc types (e.g. INV, PL, COA), you MUST treat it as a **multi-type document**.\n"
            "5. If only one doc type is found, it's **single-type**.\n\n"

            "**Field Extraction by Type:**\n"
            "- **DN / PL** → `Doc Type`, `PO#`, `DN#`, `Supplier`\n"
            "- **INV** → `Doc Type`, `PO#`, `DN#`, `Supplier`, `INV NO#`\n"
            "- **COA**, **Bill of Lading**, **Air Waybill** → `Doc Type`, `Supplier`\n\n"

            "**Supplier Detection Guidance:**\n"
            "- In DN: Look after 'Deliver to'\n"
            "- In INV: Look after 'Supplied by' (never 'Sold to')\n"
            "- Clean up supplier names. For example, if value is:\n"
            "  'BRANCH OF ZUELLIG PHARMA VIETNAM LT', extract just 'ZUELLIG PHARMA VIETNAM LT'\n\n"

            "**Final Output Format:**\n"
            "- Return a valid JSON array.\n"
            "- Each object = one document.\n"
            "- Use fields: `Doc Type`, `PO#`, `DN#`, `INV NO#`, `Supplier`\n"
            "- Only include fields that are applicable to the document type.\n"
            "- If a field is missing, omit it (don’t leave it empty or null).\n\n"

            "**Now, analyze the following document:**\n"
            f"{', '.join(parsed_text)}\n\n"

            "**Remember:**\n"
            "- Skip irrelevant pages\n"
            "- Treat PL as DN and rename fields accordingly\n"
            "- Do not miss any document section\n"
            "- Do not duplicate document types unless it's clear there are multiple of the same kind\n"
            "- Return clean, concise JSON as per format"
        )   





    return prompt
def create_dn_prompt_from_text(parsed_text):
    # fields = ['PO#','PL#','INV Item Count', 'COA Item Count','Supplier','Email Address','Supplier Flag','Supplier Estimate Name', 'DN#','Item Code' ,  'Quantity', 'Batch#', 'Document Date', 'Incoterms', 'Date of loading', ' Executed on', 'Batch#', 'Manufacturing Date', 'Expiry Date', 'Best Before Date', 'Date of receipt','Posting Date',  'Packing Slip#', 'INV NO#']
    fields = ['PO#', 'Item Code','Packing Slip#','Quantity','Batch#','Manufacturing Date', 'Expiry Date', 'Document Date', 'Supplier Name', 'Incoterm', 'Item Description']
    # "1. Purchase order number
    # 2. Item codes (Vendor and/or Menarini)
    # 3. Packing slip number
    # 4. Shipped quantity for each item 
    # 5. Batch number for each item
    # 6. Manufacturing date for each item/batch
    # 7. Expiry date  for each item/batch
    # 8. Document date
    # 9. Supplier/Vendor Name
    # 10. Incoterm
    # 11. item description"
    # Construct the prompt with flexibility for various formats and languages
    prompt = (
        "This document is DN."
        f"{', '.join(parsed_text)}.\n\n"
        "Please get these field."
        f"{', '.join(fields)}.\n\n"
        "The PO# is one or several."
        "And for one PO# there is one or several Items."

        "The Quantity is number. So give me only number without unit like `KG` or so on."
        "As the result of uncorrect ocr, the PO# can be expressed like 'Po1-12324' or 'P0-12312' or 'P0O1-12312'."
        "The PO# format is like this, PO123-1234. Not 'Po' or 'P0O1' or 'P0' before '-'. So if the PO# is not correct, update it."
        "The Batch# can be expressed like these in document..\n"
        "Batch / Batch No. / Lot / Lot No. / Lot #\n\n"
        
        "The Manufacturing Date can be expressed like these in document..\n"
        "Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n\n"

        "The Expiry Date can be expressed like these in document.\n"
        "Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n\n"

        "The Quantity can be expressed like these in document.\n"
        "Quantity / Shipped Quantity / Quantity Shipped / Despatched Quantity / Quantity Depatched / Delivered"

        "The Packing Slip# can be expressed like these in document\n"
        "Delivery Note / Despatch Note / DN / D/N / Packing List / P/L / Packing Slip\n\n"

        "The Item Code can be expressed like these in document\n"
        "Item / Item No. / Item Number / Customer Reference Code / Cust. Ref. Code / Product No. / Product Code / Product Number / Material Code / Material No. / Customer Part Code\n\n"

        "The Incoterm can be expressed like these in document\n"
        "Incoterms / Shipping Terms\n\n"

        "\nImportant Rule:\n"
        "These are e.g value for each fields. Look carfully about the expression form for each value."

        "Item Code : RBMENNEBVN0004\n"
        "Quantity : 46660 (* there is no `KG` or other unit. Remove the `,` for quantity. It must be int for cacluate.)\n"
        "Batch# : 31303B\n"
        
        "Item Description:NEBILET 5MG 14TABS VN SALES (VIETNAM)\n"
        "Expiry Date : 09/02/2026\n"
        "PO#: PO22-00014\n"

        "So if there is mistake in the document, correct them as right form. Carfully consider the difference between `0` and `O` , `1` and `l`."

        "Please return the extracted information as a JSON object."
        "Ensure your response follows this JSON format exactly."
        "Please send me data as like this."
        "[\n"
                "   {\n"
                "     \"PO#\": \"1345245\",\n"
                "     \"Item Code:\": \"Q1234\",\n"
                "   }\n"
        "]\n"
    )
    return prompt


def create_inv_prompt_from_text(parsed_text):
    # fields = ['PO#','PL#','INV Item Count', 'COA Item Count','Supplier','Email Address','Supplier Flag','Supplier Estimate Name', 'DN#','Item Code' ,  'Quantity', 'Batch#', 'Document Date', 'Incoterms', 'Date of loading', ' Executed on', 'Batch#', 'Manufacturing Date', 'Expiry Date', 'Best Before Date', 'Date of receipt','Posting Date',  'Packing Slip#', 'INV NO#']
    fields = ['PO#', 'Item Code','Packing Slip#','Quantity','Batch#','Manufacturing Date', 'Expiry Date', 'Document Date', 'Supplier Name', 'Incoterm','Invoice Number','Item Description']
    # "1. Purchase order number
    # 2. Item codes (Vendor and/or Menarini)
    # 3. Packing slip number
    # 4. Shipped quantity for each item 
    # 5. Batch number for each item
    # 6. Manufacturing date for each item/batch
    # 7. Expiry date  for each item/batch
    # 8. Document date
    # 9. Supplier/Vendor Name
    # 10. Incoterm
    # 11. Invoice number
    # 12. item description"
    prompt = (
        "This document is INV."
        f"{', '.join(parsed_text)}.\n\n"
        "Please get these field."
        f"{', '.join(fields)}.\n\n"
        "The PO# is one or several."
        "And for one PO# there is one or several Items."
        "The Quantity is number. So give me only number without unit like `KG` or so on."

        "The Batch# can be expressed like these in document..\n"
        "Batch / Batch No. / Lot / Lot No. / Lot #\n\n"
        
        "The Manufacturing Date can be expressed like these in document.\n"
        "Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n\n"

        "The Expiry Date can be expressed like these in document.\n"
        "Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n\n"

        "The Quantity can be expressed like these in document.\n"
        "Quantity / Shipped Quantity / Quantity Shipped / Despatched Quantity / Quantity Depatched / Delivered"

        "The Packing Slip# can be expressed like these in document\n"
        "Delivery Note / Despatch Note / DN / D/N / Packing List / P/L / Packing Slip\n\n"
        
        "The Item Code can be expressed like these in document\n"
        "Item / Item No. / Item Number / Customer Reference Code / Cust. Ref. Code / Product No. / Product Code / Product Number / Material Code / Material No. / Customer Part Code\n\n"

        "The Invoice Number can be expressed like these in document.\n"
        "Invoice / Tax Invoice / Tax Inv. / Commercial Invoice / Commercial Inv.\n\n"

        "The Incoterm can be expressed like these in document\n"
        "Incoterms / Shipping Terms\n\n"

        "\nImportant Rule:\n"
        "The PO# can be expressed like these - `P0-123456` or `PO01-123456` or `P0O1-2313` or `Po-32531`"
        "But the exact PO# expression is like this - `PO1-123456` or `PO12-123456`"
        "These are e.g value for each fields. Look carfully about the expression form for each value."

        "Item Code : RBMENNEBVN0004\n"
        "Quantity : 46660 (* there is no `KG` or other unit. Remove the `,` for quantity. It must be int for cacluate.)\n"
        "Batch# : 31303B\n"
        "Item Description:NEBILET 5MG 14TABS VN SALES (VIETNAM)\n"
        "Expiry Date : 09/02/2026\n"
        "PO#: PO22-00014\n"

        "So if there is mistake in the document, correct them as right form. Carfully consider the difference between `0` and `O` , `1` and `l`."

        "Please return the extracted information as a JSON object."
        "Ensure your response follows this JSON format exactly."
        "Please send me data as like this."
        "[\n"
                "   {\n"
                "     \"PO#\": \"1345245\",\n"
                "     \"Item Code\": \"Q1234\",\n"
                "   }\n"
        "]\n"
    )
    return prompt


def create_coa_prompt_from_text(parsed_text):
    fields = ['Item Description', 'Manufacturing Date', 'Expiry Date', 'Batch#']
    
    prompt = (
        "This document is a COA (Certificate of Analysis).\n"
        f"{', '.join(parsed_text)}\n\n"
        
        "Please extract the following fields for each item in the document:\n"
        f"{', '.join(fields)}\n\n"
        
        "These fields can appear in various forms:\n"
        "- Manufacturing Date: Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n"
        "- Expiry Date: Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n"
        "- Batch#: Batch / Batch Number / Batch No. / Lot / Lot No. / Lot #\n"
        "- Item Description: A descriptive name of the product/item\n\n"
        
        "Example values:\n"
        "- Batch#: 31303B\n"
        "- Item Description: NEBILET 5MG 14TABS VN SALES (VIETNAM)\n"
        "- Manufacturing Date: 09/02/2023\n"
        "- Expiry Date: 09/02/2026\n\n"
        
        "Please return the extracted data as a JSON array of objects, like this:\n"
        "[\n"
        "  {\n"
        "    \"Item Description\": \"NEBILET 5MG 14TABS VN SALES (VIETNAM)\",\n"
        "    \"Manufacturing Date\": \"09/02/2023\",\n"
        "    \"Expiry Date\": \"09/02/2026\",\n"
        "    \"Batch#\": \"31303B\"\n"
        "  }\n"
        "]\n"
    )
    
    return prompt


def create_bol_prompt_from_text(parsed_text):
    # fields = ['PO#','PL#','INV Item Count', 'COA Item Count','Supplier','Email Address','Supplier Flag','Supplier Estimate Name', 'DN#','Item Code' ,  'Quantity', 'Batch#', 'Document Date', 'Incoterms', 'Date of loading', ' Executed on', 'Batch#', 'Manufacturing Date', 'Expiry Date', 'Best Before Date', 'Date of receipt','Posting Date',  'Packing Slip#', 'INV NO#']
    
    fields = ['Incoterm','Posting Date']
    prompt = (
        "This document is Bill of Lading or Air Waybill."
        f"{', '.join(parsed_text)}.\n\n"
        "Please get these field."
        f"{', '.join(fields)}.\n\n"

        "The Posting Date can be expressed like these in document.\n\n"
        "Posting Date/Shipped On Board Date / ETD / On Board Date / Executed On / Flight/Date / Place and date of issue / Requested Flight Date\n\n"

        "The Incoterm can be expressed like these in document\n"
        "Incoterms / Shipping Terms\n\n"

        "Please return the extracted information as a JSON object."
        "Ensure your response follows this JSON format exactly."
        "Please send me data as like this."
        "[\n"
                "   {\n"
                "     \"Incoterm\": \"1345245\",\n"
                "     \"Posting Date\": \"Q1234\",\n"
                "   }\n"
        "]\n"
    )
    return prompt

def create_multi_prompt_from_text(parsed_text, doc_types):
    # fields = ['PO#','PL#','INV Item Count', 'COA Item Count','Supplier','Email Address','Supplier Flag','Supplier Estimate Name', 'DN#','Item Code' ,  'Quantity', 'Batch#', 'Document Date', 'Incoterms', 'Date of loading', ' Executed on', 'Batch#', 'Manufacturing Date', 'Expiry Date', 'Best Before Date', 'Date of receipt','Posting Date',  'Packing Slip#', 'INV NO#']
    dn_fields = ['PO#', 'Item Code','Packing Slip#','Quantity','Batch#','Manufacturing Date', 'Expiry Date', 'Document Date', 'Supplier Name', 'Incoterm', 'Item Description']
    inv_fields = ['PO#', 'Item Code','Packing Slip#','Quantity','Batch#','Manufacturing Date', 'Expiry Date', 'Document Date', 'Supplier Name', 'Incoterm','Invoice Number','Item Description']
    coa_fields = ['Item Description','Manufacturing Date', 'Expiry Date','Batch#']
    bol_fields = ['Incoterm','Posting Date']
    # "1. Item Code
    # 2. Item Description
    # 3. Manufacturing date
    # 4. Expiry Date
#   1. Incoterm
#   2. Posting Date"
    prompt = (
        f"This document contains several document - {doc_types}."
        f"{', '.join(parsed_text)}.\n\n"
        
        "Please get these field in DN part."
        f"{', '.join(dn_fields)}.\n\n"
        "The PO# is one or several."
        "And for one PO# there is one or several Items."

        "The Quantity is number. So give me only number without unit like `KG` or so on."

        "The Batch# can be expressed like these in document..\n"
        "Batch / Batch No. / Lot / Lot No. / Lot #\n\n"
        
        "The Manufacturing Date can be expressed like these in document..\n"
        "Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n\n"

        "The Expiry Date can be expressed like these in document.\n"
        "Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n\n"

        "The Quantity can be expressed like these in document.\n"
        "Quantity / Shipped Quantity / Quantity Shipped / Despatched Quantity / Quantity Depatched / Delivered"

        "The Packing Slip# can be expressed like these in document\n"
        "Delivery Note / Despatch Note / DN / D/N / Packing List / P/L / Packing Slip\n\n"

        "The Item Code can be expressed like these in document\n"
        "Item / Item No. / Item Number / Customer Reference Code / Cust. Ref. Code / Product No. / Product Code / Product Number / Material Code / Material No. / Customer Part Code\n\n"
        
        "Please get these field in INV part."
        f"{', '.join(inv_fields)}.\n\n"
        "The PO# is one or several."
        "And for one PO# there is one or several Items."

        "The Quantity is number. So give me only number without unit like `KG` or so on."

        "The Batch# can be expressed like these in document..\n"
        "Batch / Batch No. / Lot / Lot No. / Lot #\n\n"
        
        "The Manufacturing Date can be expressed like these in document.\n"
        "Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n\n"

        "The Expiry Date can be expressed like these in document.\n"
        "Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n\n"

        "The Quantity can be expressed like these in document.\n"
        "Quantity / Shipped Quantity / Quantity Shipped / Despatched Quantity / Quantity Depatched / Delivered"

        "The Packing Slip# can be expressed like these in document\n"
        "Delivery Note / Despatch Note / DN / D/N / Packing List / P/L / Packing Slip\n\n"
        
        "The Item Code can be expressed like these in document\n"
        "Item / Item No. / Item Number / Customer Reference Code / Cust. Ref. Code / Product No. / Product Code / Product Number / Material Code / Material No. / Customer Part Code\n\n"

        "The Invoice Number can be expressed like these in document.\n"
        "Invoice / Tax Invoice / Tax Inv. / Commercial Invoice / Commercial Inv.\n\n"
        
        "Please get these field in COA part."
        f"{', '.join(coa_fields)}.\n\n"

        "The Manufacturing Date can be expressed like these in document.\n"
        "Manufacturing Date / Mfg Date / Produced On / MD / Manufacture Date / Date of Manufacture\n\n"

        "The Expiry Date can be expressed like these in document.\n"
        "Expiry Date / Exp Date / ED / Best Before Date / Date of Expiry / Retest Date\n\n"
        
        "The Batch# can be expressed like these in document..\n"
        "Batch / Batch No. / Lot / Lot No. / Lot #\n\n"
        
        "Please get these field in Bill of Lading and Air Waybill part."
        f"{', '.join(bol_fields)}.\n\n"
        "The Posting Date can be expressed like these in document.\n\n"
        "Posting Date/Shipped On Board Date / ETD / On Board Date / Executed On / Flight/Date / Place and date of issue / Requested Flight Date\n\n"
        
        "Please return the extracted information as a JSON object."
        "Ensure your response follows this JSON format exactly."
        "Please send me data as like this."
        "[\n"
            "[\n"
                "   {\n"
                "     \"Doc Type\": \"INV\",\n"
                "     \"PO#\": \"1345245\",\n"
                "     \"Item Code\": \"Q1234\",\n"
                "   },\n"
            "],\n"
            
            
            "[\n"
                "   {\n"
                "     \"Doc Type\": \"DN\",\n"
                "     \"PO#\": \"1345245\",\n"
                "     \"Item Code\": \"Q1234\",\n"
                "   },\n"
            "],\n"
            
        "]\n"
    )
    return prompt
def extract_fields_using_gpt(text_data, prompt_type, doc_types):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_KEY}",
    }
    if prompt_type == 0:
        prompt = text_data
    elif prompt_type == 1:
        prompt = create_prompt_from_text(text_data)
    elif prompt_type == 2:
        prompt = create_dn_prompt_from_text(text_data)
    elif prompt_type == 3:
        prompt = create_inv_prompt_from_text(text_data)
    elif prompt_type == 4:
        prompt = create_coa_prompt_from_text(text_data)
    elif prompt_type == 5:
        prompt = create_bol_prompt_from_text(text_data)
    elif prompt_type == 6:
        prompt = create_multi_prompt_from_text(text_data, doc_types)
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            },
        ],
        "max_tokens": 4096,  # Adjust this if needed
        "temperature": 0
    }

    response = requests.post(OPENAI_API_URL, headers=headers, json=payload, proxies=PROXIES)
    
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
    
    extracted_fields = extract_fields_using_gpt(text_data, 1, "")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_fields, f, ensure_ascii=False, indent=4)

    print(f"Extracted fields with positions saved to {output_path}")
    
    return extracted_fields

def extract_document_field(txt_path, output_path, doc_type, doc_types):
    text_data = load_text_from_txt(txt_path)
    
    extracted_fields = extract_fields_using_gpt(text_data, doc_type,doc_types)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(extracted_fields, f, ensure_ascii=False, indent=4)

    print(f"Extracted fields with positions saved to {output_path}")
    
    return extracted_fields
def get_basic_data(text_data):
    basic_detail = extract_fields_using_gpt(text_data, 0, "")
    return basic_detail