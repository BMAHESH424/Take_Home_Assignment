import os
import faiss
import json
from groq import Groq
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List
from sentence_transformers import SentenceTransformer

# Load credentials
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY not found in .env file.")

# Initialize Groq Client
client = Groq(api_key=api_key)

app = FastAPI()
model = None; index = None; metadata = None

def load_resources():
    global model, index, metadata
    if os.path.exists("catalog.index") and os.path.exists("catalog_metadata.json"):
        model = SentenceTransformer('all-MiniLM-L6-v2')
        index = faiss.read_index("catalog.index")
        with open("catalog_metadata.json", "r") as f:
            metadata = json.load(f)
        return True
    return False

load_resources()

class Message(BaseModel):
    role: str; content: str
class ChatRequest(BaseModel):
    messages: List[Message]

@app.get("/health")
def health(): return {"status": "ok"}

@app.get("/")
async def read_index(): return FileResponse('static/index.html')
@app.get("/style.css")
async def read_style(): return FileResponse('static/style.css')
@app.get("/script.js")
async def read_script(): return FileResponse('static/script.js')

@app.post("/chat")
async def chat(request: ChatRequest):
    if not index:
        if not load_resources():
            raise HTTPException(status_code=500, detail="Catalog not indexed.")

    # 1. RAG Retrieval
    history_text = " ".join([m.content for m in request.messages])
    query_vec = model.encode([history_text]).astype('float32')
    _, indices = index.search(query_vec, k=10)
    retrieved_context = [metadata[idx] for idx in indices[0] if idx != -1]

    # 2. PROMPT: Maintained with double braces for f-string literal JSON
    prompt = f"""
    SYSTEM: You are an SHL Assessment specialist. 
    TASK: Guide the user to a shortlist of 1-10 assessments from the catalog.
    **agent that takes the user from a vague intent (“I am hiring a Java developer”) to
    a grounded shortlist of SHL assessments through dialogue. The agent should clarify when needed, accept refinement,
    support comparison between assessments, and never recommend anything outside the SHL catalog.**
    
    CATALOG CONTEXT:
    {json.dumps(retrieved_context)}

    HISTORY:
    {json.dumps([m.dict() for m in request.messages])}

    OUTPUT STRICT JSON FORMAT:
    {{
      "reply": "string",
      "recommendations": [{{"name": "string", "url": "string", "test_type": "string"}}],
      "end_of_conversation": boolean
    }}
    """

    try:
        # 3. Groq Completion Call
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile", # Groq's high-performance model
            response_format={"type": "json_object"} # Ensures valid JSON output
        )
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Groq Error: {e}")
        return {
            "reply": "Could you please clarify the role and level?", 
            "recommendations": [], 
            "end_of_conversation": False
        }
