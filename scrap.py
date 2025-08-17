import json
from utils.gemini_client import call_gemini

def is_scraping_needed(questions: str) -> dict:
    if not isinstance(questions, str) or not questions.strip():
        raise ValueError("questions must be a non-empty string.")

    system_prompt = """
You are a decision-making AI.

Rules:
1. Only set "search" to true if the query explicitly asks to look something up online and does NOT include any web URL or local file reference.
2. Only set "scraping" to true if the query contains one or more web URLs starting with "http://" or "https://".
3. Local file references (e.g., .csv, .txt, /path/to/file) must NOT trigger search or scraping. In such cases, set "search": false and "scraping": false.
4. If "scraping" is false, "urls" must be an empty list.
5. Output STRICT JSON only in the format:
{
  "search": true/false,
  "query": "<search query or empty string>",
  "scraping": true/false,
  "urls": ["<url1>", "<url2>"]
}
No explanation, no extra text.
"""

    response_schema = {
        "type": "object",
        "properties": {
            "search": {"type": "boolean"},
            "query": {"type": "string"},
            "scraping": {"type": "boolean"},
            "urls": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["search", "query", "scraping", "urls"]
    }

    raw_response = call_gemini(
        model="gemini-2.5-flash-lite",
        system_prompt=system_prompt,
        user_prompt=questions,
        response_schema=response_schema,
        response_mime_type="application/json",
        stream=False
    )

    try:
        parsed = json.loads(raw_response)
    except Exception as e:
        raise ValueError(f"Invalid JSON returned from Gemini: {raw_response}")

    # Final shape validation
    if not isinstance(parsed.get("urls", []), list):
        raise ValueError("Invalid format: 'urls' must be a list.")

    return parsed