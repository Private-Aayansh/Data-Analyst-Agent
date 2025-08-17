from fastapi import FastAPI, UploadFile, File, Request, HTTPException
from fastapi.responses import JSONResponse
from answer import get_answer
from fastapi.middleware.cors import CORSMiddleware
from utils.openai_client import call_openai
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api")
async def analyze(request: Request):
    """
    Example request:
    curl "https://app.example.com/api/" \
         -F "questions.txt=@questions.txt" \
         -F "image.png=@image.png" \
         -F "data.csv=@data.csv"
    """

    form = await request.form()
    questions: UploadFile | None = None
    files: list[UploadFile] = []

    for key, value in form.items():
        if hasattr(value, "filename") and value.filename:
            if value.filename.endswith(".txt"):
                questions = value
                # print(f"📄 Found questions file: {value.filename}")
            else:
                files.append(value)
                # print(f"📂 Extra file: field={key}, filename={value.filename}")
        else:
            print(f"🔤 Text field: {key}, value={value}")

    if not questions:
        raise HTTPException(status_code=400, detail="Missing questions file (.txt)")

    # Read the questions.txt into string
    questions_text = (await questions.read()).decode("utf-8-sig")
    # print(questions)
    # print(questions_text)
    print("received files", files)

    try:
        answers = get_answer(questions_text, files or [])
        print(answers)
        final_answers = call_openai(questions, answers)
        try:
            final_answers = json.loads(final_answers)  # parse back into dict
        except json.JSONDecodeError:
            final_answers = {"result": final_answers}
        return JSONResponse(content=final_answers)
    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)
