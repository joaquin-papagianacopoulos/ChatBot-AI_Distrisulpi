from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM
from groq import Groq
import os
from typing import List, Optional
import uuid

class GroqLLM(LLM):
    client: Groq
    model: str = "mixtral-8x7b-32768"
    
    def __init__(self):
        super().__init__()
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=0,
            max_tokens=1024
        )
        return response.choices[0].message.content
    
    @property
    def _llm_type(self) -> str:
        return "groq"

class RAGSystem:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.chunker = SemanticChunker(
            embeddings=self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=95
        )
        
        self.vectorstore = Chroma(
            persist_directory="./chroma_db",
            embedding_function=self.embeddings
        )
        
        self.llm = GroqLLM()
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(search_kwargs={"k": 3})
        )
    
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
        
        chunks = self.chunker.split_text(text)
        
        documents = [
            Document(
                page_content=chunk,
                metadata={"file_id": file_id, "chunk_id": str(uuid.uuid4())}
            )
            for chunk in chunks
        ]
        
        self.vectorstore.add_documents(documents)
    
    async def query(self, question: str, file_id: Optional[str] = None) -> str:
        if file_id:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={
                    "k": 3,
                    "filter": {"file_id": file_id}
                }
            )
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever
            )
            return qa_chain.run(question)
        else:
            return self.qa_chain.run(question)