from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
from typing import List
import transformers
import torch
import boto3
import json
import re
from pdf_parser.pdf_to_text import *
from OCR.process_image import *
s3 = boto3.client('s3')

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks
sys.path.append(os.path.join(os.path.dirname(__file__), "pdf_parser"))
sys.path.append(os.path.join(os.path.dirname(__file__), "OCR"))
# Load environment variables from a .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
bucket_name = os.getenv("BUCKET_NAME")


def count_tokens(text: str) -> int:
    tokens = re.findall(r'\S+|\n', text)
    return len(tokens)
def generate_prompt(query: str) -> str:
    """
    Generate a prompt for the LLM using the user's query and retrieved context.

    Args:
        query (str): The original user query.
        retrieved_context (List[str]): List of retrieved items from the RAG retriever.

    Returns:
        str: A detailed prompt to be sent to the LLM.
    """

    
    prompt = (
        "You are a shopping assistant that helps users create detailed shopping lists based on their needs.\n"
        f"The user provided the following query:\n"
        f"{query}\n\n"
        "Please follow this format for your response:\n"
        "1. Shopping list: **only** return the shopping list in this format:\n"
        "{\n"
        '"item_name_1": "quantity_1",\n'
        '"item_name_2": "quantity_2",\n'
        "...}\n"
        " - For liquid items, specify the quantity in milliliters (e.g., 'milk': '1000 ml').\n"
        " - For items that require grams, specify the quantity in grams (e.g., 'flour': '500 gr').\n"
        " - For other items, use 'units' as the quantity type (e.g., 'bananas': '7 units').\n"
        "Do not include any additional text or comments outside of the dictionary format."
    )
    return prompt

def get_response(prompt):
    complite_prompt = generate_prompt(prompt)
    client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), 
        )

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": complite_prompt,
        }],
        model="gpt-4o-mini",
        max_tokens=count_tokens(complite_prompt)
    )
    generated_text = response.choices[0].message.content

    return generated_text


def lambda_handler(event,context):

    key = event.get('filename')
    prompt_from_user = event.get('query')
    flag = event.get('flag')
    if flag==1:
        #check type of file:
        file_extension = key.split('.')[-1].lower()
        #reading from s3 file
        obj_from_s3 = s3.get_object(Bucket=bucket_name,Key=key)
        file_content = obj_from_s3['Body'].read()
        #file is pdf
        if file_extension=="pdf":
            pdf_processor = pdf_To_Text(file_content)
            text = pdf_processor.get_text()
        elif file_extension in ['jpg', 'jpeg', 'png']:
            ocr_processor = OCR_to_heb(file_content)
            text = ocr_processor.get_text()
        result_from_llm = get_response(text)
    else:
        result_from_llm = get_response(prompt_from_user)
    return {"body":result_from_llm,"statusCode":200}
    
