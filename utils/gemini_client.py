import os
import time
import threading
import queue
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY is not set in environment variables.")

client = genai.Client(api_key=API_KEY)

def call_gemini(
    model: str,
    system_prompt: str,
    user_prompt: str,
    thinking_budget: int = 0,
    response_schema=None,
    response_mime_type=None,
    tools=None,
    stream=False,
    timeout=80,
    file_refs: list[str] | None = None
):
    start_time = time.time()

    # This queue will store streamed outputs
    output_queue = queue.Queue()
    finished_flag = threading.Event()

    if not user_prompt or not isinstance(user_prompt, str):
        raise ValueError("user_prompt must be a non-empty string.")
    
    def worker():
        try:
            system_instructions = types.Content(
                role="system",
                parts=[types.Part.from_text(text=system_prompt or "")]
            )

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=user_prompt)]
                )
            ]

            if file_refs:
                for file_obj in file_refs:
                    contents[0].parts.append(
                        types.Part(file_data=types.FileData(file_uri=file_obj.uri))
                    )

            generate_content_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
                system_instruction=system_instructions
            )

            if response_schema:
                generate_content_config.response_schema = response_schema
            if response_mime_type:
                generate_content_config.response_mime_type = response_mime_type
            if tools:
                generate_content_config.tools = tools

            parts_output = []

            if stream:
                for chunk in client.models.generate_content_stream(
                    model=model,
                    contents=contents,
                    config=generate_content_config,
                ):
                    if (
                        not chunk.candidates
                        or not chunk.candidates[0].content
                        or not chunk.candidates[0].content.parts
                    ):
                        continue

                    part = chunk.candidates[0].content.parts[0]

                    if part.text:
                        # print(part.text)
                        parts_output.append(f"{part.text}")
                        output_queue.put(f"{part.text}")
                    # if part.executable_code:
                    #     print(part.executable_code)
                    #     parts_output.append(f"[CODE]\n{part.executable_code}")
                    #     output_queue.put(f"[CODE]\n{part.executable_code}")

                    if part.code_execution_result:
                        # print(part.code_execution_result)
                        parts_output.append(f"[CODE_RESULT]\n{part.code_execution_result}")
                        output_queue.put(f"[CODE_RESULT]\n{part.code_execution_result}")

            else:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=generate_content_config
                )
                print(response)
                parts_output.append(response.text)
                output_queue.put(response.text)

            finished_flag.set()

        except Exception as e:
            output_queue.put(f"[ERROR] {e}")
            finished_flag.set()

    # Run worker in a thread
    t = threading.Thread(target=worker, daemon=True)
    t.start()

    collected = []
    while time.time() - start_time < timeout:
        try:
            item = output_queue.get(timeout=1)
            collected.append(item)
        except queue.Empty:
            if finished_flag.is_set():
                break
            continue

    # 🔑 Drain anything left in the queue after timeout
    while not output_queue.empty():
        collected.append(output_queue.get())

    if not collected:
        return "[TIMEOUT] No output received."

    return "\n".join(collected)