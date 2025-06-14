from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from groq import Groq
import os
import pickle
from typing import List, Optional, Dict
import uuid

class SimpleRAGSystem:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.documents = {}
        self.embeddings = {}
        self.chunks = {}
    
    def semantic_chunk(self, text: str, max_chunk_size: int = 1000) -> List[str]:
        sentences = text.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < max_chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def add_document(self, file_id: str, file_path: str):
        from utils.pdf_utils import extract_text_from_pdf
        from utils.excel_utils import extract_text_from_excel
        
        if file_path.endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            text = extract_text_from_excel(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        
        chunks = self.semantic_chunk(text)
        embeddings = self.model.encode(chunks)
        
        self.documents[file_id] = text
        self.chunks[file_id] = chunks
        self.embeddings[file_id] = embeddings
    
    async def query(self, question: str, file_id: Optional[str] = None) -> str:
        question_embedding = self.model.encode([question])
        
        if file_id and file_id in self.embeddings:
            similarities = cosine_similarity(question_embedding, self.embeddings[file_id])[0]
            best_chunks_idx = np.argsort(similarities)[-3:][::-1]
            context = "\n".join([self.chunks[file_id][i] for i in best_chunks_idx])
        else:
            all_chunks = []
            all_embeddings = []
            for fid in self.embeddings:
                all_chunks.extend(self.chunks[fid])
                all_embeddings.extend(self.embeddings[fid])
            
            if not all_embeddings:
                context = ""
            else:
                similarities = cosine_similarity(question_embedding, all_embeddings)[0]
                best_chunks_idx = np.argsort(similarities)[-3:][::-1]
                context = "\n".join([all_chunks[i] for i in best_chunks_idx])
        
        prompt = f"""
        Context: {context}
        
        Question: {question}
        
        Answer based on the context provided. If the context doesn't contain relevant information, say so.
        """
        
        response = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0,
            max_tokens=1024
        )
        
        return response.choices[0].message.content