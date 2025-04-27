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
    "You are a shopping assistant that builds a precise shopping list based only on the user’s request "
    "and any uploaded file text. Do NOT add or infer any extra items.\n\n"
    "User request:\n"
    f"{query}\n\n"
    "Uploaded file text (if empty, ignore):\n"
    f"{text}\n\n"
    "Extract only the products explicitly mentioned, preserving required quantities when specified "
    "(or assign a reasonable default if none given).\n\n"
    "Then output a single JSON object whose keys are department names and whose values are lists of items "
    "for that department. Use exactly these departments (and no others):\n"
    "['baby_products', 'bakery', 'beverages', 'cleaning_products', 'dairy_products', "
    "'dry_goods', 'frozen_foods', 'fruits_and_vegetables', 'health_and_beauty', "
    "'home_and_garden', 'meat_and_fish', 'pet_products', 'ready_meals', "
    "'snacks_and_sweets', 'spices_and_additives']\n\n"
    "– Do NOT include a department key if it has no matching items.\n"
    "– Each item entry should be an object with 'name' and 'quantity'.\n\n"
    "Output format (valid JSON):\n"
    "{\n"
    '  "department_name": [\n'
    '    { "name": "Item A", "quantity": "X" },\n'
    '    { "name": "Item B", "quantity": "Y" }\n'
    '  ],\n'
    '  "another_department": [ ... ]\n'
    "}\n"
    )
    return prompt
def generate_basic_list_prompt(query,text):
    if text ==None:
        text=""
    prompt = (
    "You are a shopping assistant that builds a precise shopping list based only on the user’s request "
    "and any uploaded file text. Do NOT add or infer any extra items.\n\n"
    "User request:\n"
    f"{query}\n\n"
    "Uploaded file text (if empty, ignore):\n"
    f"{text}\n\n"
    "Extract only the products explicitly mentioned, preserving required quantities when specified "
    "(or assign a reasonable default if none given).\n\n"
    "Then output a single JSON object whose keys are department names and whose values are lists of items "
    "for that department. Use exactly these departments (and no others):\n"
    "['baby_products', 'bakery', 'beverages', 'cleaning_products', 'dairy_products', "
    "'dry_goods', 'frozen_foods', 'fruits_and_vegetables', 'health_and_beauty', "
    "'home_and_garden', 'meat_and_fish', 'pet_products', 'ready_meals', "
    "'snacks_and_sweets', 'spices_and_additives']\n\n"
    "– Do NOT include a department key if it has no matching items.\n"
    "– Each item entry should be an object with 'name' and 'quantity'.\n\n"
    "Output format (valid JSON):\n"
    "{\n"
    '  "department_name": [\n'
    '    { "name": "Item A", "quantity": "X" },\n'
    '    { "name": "Item B", "quantity": "Y" }\n'
    '  ],\n'
    '  "another_department": [ ... ]\n'
    "}\n"
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
        model="o4-mini",
        
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

    

