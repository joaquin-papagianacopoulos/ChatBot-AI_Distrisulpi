from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
from typing import List, Optional
import tempfile
import shutil

from models.rag_system import RAGSystem
from models.file_processor import FileProcessor

app = FastAPI(title="Chatbot RAG Converter")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_system = RAGSystem()
file_processor = FileProcessor()

class ChatMessage(BaseModel):
    message: str
    file_id: Optional[str] = None

class ConversionRequest(BaseModel):
    file_id: str
    target_format: str
    instructions: Optional[str] = None

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        file_id = await file_processor.process_file(tmp_path, file.filename)
        await rag_system.add_document(file_id, tmp_path)
        
        os.unlink(tmp_path)
        
        return {"file_id": file_id, "filename": file.filename, "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        response = await rag_system.query(message.message, message.file_id)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert")
async def convert_file(request: ConversionRequest):
    try:
        output_path = await file_processor.convert_file(
            request.file_id, 
            request.target_format, 
            request.instructions
        )
        return FileResponse(output_path, media_type='application/octet-stream')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def list_files():
    try:
        files = await file_processor.list_files()
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))