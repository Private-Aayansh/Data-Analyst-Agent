import time
import mimetypes
from typing import List
from fastapi import UploadFile
from concurrent.futures import ThreadPoolExecutor, as_completed
from google.genai import types
from utils.gemini_client import call_gemini
from utils.tavily_client import tavily_search, tavily_scrap
from scrap import is_scraping_needed

def get_answer(questions: str, files: List[UploadFile]):
    duration, start_time = 150, time.time()
    is_scraping_needed_response = is_scraping_needed(questions)

    scraping_results = []
    if is_scraping_needed_response.get("search"):
        tavily_search_response = tavily_search(is_scraping_needed_response.get("query"))
        # print(tavily_search_response)
        scraping_results.append(tavily_search_response)

    if is_scraping_needed_response.get("scraping"):
        tavily_scrap_response = tavily_scrap(is_scraping_needed_response.get("urls"))
        # print(tavily_scrap_response)
        scraping_results.append(tavily_scrap_response)

    tools = [types.Tool(code_execution=types.ToolCodeExecution)]

    system_prompt = """
You are a data analysis agent with access to a code execution tool.

Rules:
1. Always use the code execution tool for any computation, parsing, or data processing.
2. Output must strictly match the format requested by the user (e.g., JSON, array). No explanations or extra text.
3. Never access local files or external web sources. Use only:
   - Data explicitly provided in the prompt
   - Uploaded file references (via file_refs)
   - Tavily results
4. Handling uploaded files:
   - CSV/TSV/Excel: load with pandas from the provided file reference
   - JSON: load with json from the file reference
   - TXT: read as plain text from the file reference
   - Images (e.g., PNG, JPG): load with PIL or another library from the file reference if analysis is required
   - Any other file type: attempt structured parsing if supported, otherwise return an error
5. Before returning JSON output, ensure all values are standard Python types (int, float, str, list, dict).
"""


    user_prompt = f"""
### User Questions
{questions}

### Provided Data from Tavily
{scraping_results}

### Uploaded Files
The user has provided these files: {[f.filename for f in files]}  
Use the provided file references instead of trying to open local paths.
"""
    
    uploaded_files = {}
    from google import genai
    from dotenv import load_dotenv
    import os
    load_dotenv()

    API_KEY = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=API_KEY)

    # print(files)
    for f in files:
        f.file.seek(0)
        guessed_type, _ = mimetypes.guess_type(f.filename)
        file_obj = client.files.upload(file=f.file, config={
            "display_name": f.filename,
            "mime_type": guessed_type if guessed_type else "application/octet-stream",
        })
        # print(file_obj, f.filename)
        uploaded_files[f.filename] = file_obj

    datasets = list(uploaded_files.values())
    # print(datasets)
    
    elapsed_time = time.time() - start_time
    remaining_time = max(0, duration - elapsed_time)
    print(remaining_time)

    models = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.5-pro"]
    results = ""

    # Run all calls in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_model = {
            executor.submit(
                call_gemini,
                model=m,
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                tools=tools,
                stream=True,
                thinking_budget=8000,
                timeout=remaining_time,
                file_refs=[dataset for dataset in datasets]
            ): m
            for m in models
        }

        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                results += f"{'=' * 40}\n✅ Output from {model}:\n{future.result()}\n"
            except Exception as e:
                results += f"{'=' * 40}\n❌ Error from {model}:\n[ERROR] {e}\n"

    return results

# if __name__ == "__main__":
#     answer = get_answer("""
# Analyze `sample-sales.csv`.

# Return a JSON object with keys:
# - `total_sales`: number
# - `top_region`: string
# - `day_sales_correlation`: number
# - `median_sales`: number
# - `total_sales_tax`: number

# Answer:
# 1. What is the total sales across all regions?
# 2. Which region has the highest total sales?
# 3. What is the correlation between day of month and sales? (Use the date column.)
# 4. What is the median sales amount across all orders?
# 5. What is the total sales tax if the tax rate is 10%?
# """)
#     print(answer)
    


    
