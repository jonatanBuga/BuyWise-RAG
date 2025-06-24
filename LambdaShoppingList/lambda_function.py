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
def generate_prompt(query,text):
    """
    Generate a prompt for the LLM using the user's query and retrieved context.

    Args:
        query (str): The original user query.
        retrieved_context (List[str]): List of retrieved items from the RAG retriever.

    Returns:
        str: A detailed prompt to be sent to the LLM.
    """

    if text==None:
        text=""
    prompt = (
    "You are a grocery-list assistant.\n"
    "Build an accurate shopping list based ONLY on:\n"
    "1) the user’s free-text request, and\n"
    "2) any text extracted from an uploaded file (ignore if empty).\n\n"

    "• Include every product explicitly named *and* any core ingredients that are "
    "logically required for a clearly stated dish, cuisine, or meal.  "
    "– Example: an “Italian dinner” implies pasta, tomatoes, olive oil, basil, etc.\n"
    "• Do NOT add items that are not evidently relevant.\n"
    "• Preserve stated quantities; if none, assign a reasonable default (e.g. 1 pkg / 500 g / 1 kg).\n\n"

    "— Quantity formatting rules —\n"
        "• Raw products (produce, dry goods, dairy, canned goods, etc.): specify quantity in grams.\n"
        "• Liquids: specify quantity in milliliters (ml).\n"
        "• Single-count items (tools, individual pieces, eggs, etc.): specify quantity in units.\n\n"
    "User request:\n"
    f"{query}\n\n"
    "Uploaded file text:\n"
    f"{text}\n\n"

    "Return the list as plain text—one line per item—in EXACTLY this format, in English only:\n"
    "{ Item Name : Required Quantity }\n"
    "Do not output anything before or after the list, and do not wrap it in JSON."
    )
    return prompt
def generate_basic_list_prompt(query,text):
    if text ==None:
        text=""
    prompt = (
    "You are a grocery-list assistant.\n"
    "Build an accurate shopping list based ONLY on:\n"
    "1) the user’s free-text request, and\n"
    "2) any text extracted from an uploaded file (ignore if empty).\n\n"

    "• Include every product explicitly named *and* any core ingredients that are "
    "logically required for a clearly stated dish, cuisine, or meal.  "
    "– Example: an “Italian dinner” implies pasta, tomatoes, olive oil, basil, etc.\n"
    "• Do NOT add items that are not evidently relevant.\n"
    "• Preserve stated quantities; if none, assign a reasonable default (e.g. 1 pkg / 500 g / 1 kg).\n\n"

    "User request:\n"
    f"{query}\n\n"
    "Uploaded file text:\n"
    f"{text}\n\n"

    "Return the list as plain text—one line per item—in EXACTLY this format, in English only:\n"
    "{ Item Name : Required Quantity }\n"
    "Do not output anything before or after the list, and do not wrap it in JSON."
    )
    return prompt
def get_response(prompt,type,text=None):
    if type =="full_list":
        complite_prompt = generate_prompt(prompt,text)
    elif type =="basic_list":
        complite_prompt = generate_basic_list_prompt(prompt,text)
    client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), 
        )

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": complite_prompt,
        }],
        model="gpt-4.1-mini",
        
    )
    generated_text = response.choices[0].message.content

    return generated_text


def lambda_handler(event,context):
    is_basic_list = event.get('checkBoxList') #1 mean that user want basic list
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
        if is_basic_list:
            result_from_llm = get_response(prompt_from_user,"basic_list",text)
        else:
            result_from_llm = get_response(prompt_from_user,"full_list",text)

    else:
        if is_basic_list:
            result_from_llm = get_response(prompt_from_user,"basic_list")
        else:
            result_from_llm = get_response(prompt_from_user,"full_list")

    return {"body":result_from_llm,"statusCode":200}

    

