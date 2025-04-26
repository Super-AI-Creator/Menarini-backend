import re

def extract_po_details(text, text_gen_model):
    """
    Extracts Purchase Order details from email content using Llama 3.2B.
    :param text: The email body or parsed attachment text
    :param text_gen_model: Pretrained Llama 3.2B text-generation pipeline
    :return: Dictionary containing extracted PO details
    """
    extraction_prompt = (
        f"Extract structured purchase order details from the following text:\n\n{text}\n\n"
        "Provide the output in the following format:\n"
        "- Customer PO Number:\n"
        "- Item Names:\n"
        "- Quantities:\n"
        "- Rate per Unit:\n"
        "- Units of Measurement:\n"
        "- Delivery Dates:\n"
        "- Customer Name:\n"
    )
    result = text_gen_model(extraction_prompt)
    extracted_text = result
    
    po_details = {
        "Customer PO Number": result["Purchase Order Number (PO#)"],
        "Item Names": result["Invoice Number"],
        "Quantities": result["Quantity"],
        "Rate per Unit": result["Invoice Number"],
        "Units of Measurement": result["Invoice Number"],
        "Delivery Dates": result["Document Date"],
        "Customer Name": result["Invoice Number"],
    }

    return result
