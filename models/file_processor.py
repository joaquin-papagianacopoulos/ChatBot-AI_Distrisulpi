import os
import uuid
import json
from typing import Dict, List
from utils.pdf_utils import pdf_to_excel, excel_to_pdf
from utils.excel_utils import modify_excel_with_ai
from groq import Groq

class FileProcessor:
    def __init__(self):
        self.files_db = {}
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    async def process_file(self, file_path: str, filename: str) -> str:
        file_id = str(uuid.uuid4())
        file_info = {
            "id": file_id,
            "filename": filename,
            "original_path": file_path,
            "file_type": filename.split('.')[-1].lower()
        }
        
        self.files_db[file_id] = file_info
        return file_id
    
    async def convert_file(self, file_id: str, target_format: str, instructions: str = None) -> str:
        file_info = self.files_db.get(file_id)
        if not file_info:
            raise ValueError("File not found")
        
        original_path = file_info["original_path"]
        source_format = file_info["file_type"]
        
        if source_format == "pdf" and target_format == "excel":
            output_path = pdf_to_excel(original_path)
        elif source_format in ["xlsx", "xls"] and target_format == "pdf":
            output_path = excel_to_pdf(original_path)
        else:
            raise ValueError(f"Conversion from {source_format} to {target_format} not supported")
        
        if instructions and target_format == "excel":
            output_path = await self._modify_with_ai(output_path, instructions)
        
        return output_path
    
    async def _modify_with_ai(self, file_path: str, instructions: str) -> str:
        return modify_excel_with_ai(file_path, instructions, self.groq_client)
    
    async def list_files(self) -> List[Dict]:
        return list(self.files_db.values())