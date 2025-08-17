import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in environment variables.")

url = "https://aipipe.org/openrouter/v1/chat/completions"

def call_openai(questions, answers):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    final_prompt = f"""
You are an expert at merging outputs from multiple LLMs.  
Your task: produce a single response that EXACTLY matches the format, structure, and datatypes requested by the user.

RULES:
1. Exact Structure
   - Follow the user’s requested output structure, keys, order, and formatting precisely (JSON, YAML, table, array, etc.).
   - All values must strictly match the datatype requested. If a model gives a wrong type, cast it (e.g., "12" → 12).

2. No Alteration
   - Do not invent, guess, rephrase, summarize, or drop information.
   - Copy values exactly as provided. Only adjust to enforce datatype consistency.

3. Completeness
   - If a required field is missing, return null (or an empty placeholder in the correct type).
   - Do not include error codes, failure text, or extra commentary.

4. Output Only
   - Return the final merged response only.
   - No explanations, reasoning, or preambles.

INPUTS:
- User Questions: {questions}
- Model Responses: {answers}

⚠️ Output must always be STRICTLY valid in the user’s requested format with NO deviations.
"""

    payload = {
        "model": "openai/gpt-4.1-nano",
        "messages": [
            {"role": "user", "content": final_prompt}
        ],
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    print(data["choices"][0]["message"]["content"])
    return data["choices"][0]["message"]["content"]