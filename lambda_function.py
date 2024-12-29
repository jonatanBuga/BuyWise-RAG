from openai import OpenAI
import os
import sys
from dotenv import load_dotenv
from typing import List
import transformers
import torch
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..'))) # Add the parent directory to the path sicnce we work with notebooks
# Load environment variables from a .env file
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')


def get_response(prompt):
    client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"), 
        )

    response = client.chat.completions.create(
        messages=[{"role": "system", "content": "You are a helpful assistant."},{
            "role": "user",
            "content": prompt,
        }],
        model="gpt-4o-mini",
        max_tokens=700
    )
    generated_text = response.choices[0].message.content

    return generated_text


def lambda_handler(event,context):
    query = event.get("question")

    response = get_response(query)
    print("response: ",response)

    return {"body": response , "statusCode":200}