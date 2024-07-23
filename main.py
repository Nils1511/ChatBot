from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pypdf import PdfReader
import requests
import PyPDF2

app = FastAPI()

class Query(BaseModel):
    query: str

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# Endpoint to upload PDF
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    try:
        pdf_text = extract_text_from_pdf(file.file)
        return JSONResponse(content={"pdf_text": pdf_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to ask questions
@app.post("/ask_question/")
async def ask_question(query: Query):
    pdf_text = ""  # Assume this comes from the PDF storage or is passed directly
    response = ask_llm(query.query, pdf_text)
    return JSONResponse(content={"response": response})

def ask_llm(question: str, context: str) -> str:
    # Replace with your API key and endpoint
    api_key = "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"
    api_url = "https://api-inference.huggingface.co/models/gpt2"


    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    data = {
        "inputs": f"Context: {context}\nQuestion: {question}"
    }
    
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        if "choices" in response_json and len(response_json["choices"]) > 0:
            return response_json["choices"][0].get("text", "No response")
        return "No response"
    else:
        return "Error: Could not get a response from LLM."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
