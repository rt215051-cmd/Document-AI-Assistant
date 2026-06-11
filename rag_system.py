from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import ChatOllama
from typing import List, Dict, Any
from config import Config
from pdf_processor import PDFProcessor
from embedding_manager import EmbeddingManager
from vector_store import VectorStore


class RAGSystem:
    """RAG system for PDF-based question answering."""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.pdf_processor = PDFProcessor()
        self.embedding_manager = EmbeddingManager(self.config)
        self.vector_store = VectorStore(self.config, self.embedding_manager)
        
        # Initialize Ollama LLM
        self.llm = ChatOllama(
            base_url=self.config.OLLAMA_BASE_URL,
            model=self.config.OLLAMA_MODEL,
            temperature=0.7
        )
        
        # Create retrieval chain
        self.qa_chain = self._create_qa_chain()
    
    def _create_qa_chain(self):
        """Create the RAG question-answering chain using LCEL."""
        prompt_template = """
        Use the following pieces of context from the PDF document to answer the question at the end.
        If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        retriever = self.vector_store.vectorstore.as_retriever(search_kwargs={"k": 4})
        
        qa_chain = (
            {
                "context": retriever | format_docs,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        return qa_chain
    
    def ingest_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Ingest a PDF file into the RAG system."""
        # Extract text from PDF
        text = self.pdf_processor.process_pdf(pdf_path)
        
        # Chunk the text
        chunks = self.embedding_manager.chunk_text(text)
        
        # Create documents with metadata
        documents = [
            Document(
                page_content=chunk,
                metadata={"source": pdf_path, "chunk": i}
            )
            for i, chunk in enumerate(chunks)
        ]
        
        # Add to vector store
        self.vector_store.add_documents(documents)
        
        return {
            "status": "success",
            "chunks_added": len(chunks),
            "total_documents": self.vector_store.get_collection_count()
        }
    
    def query(self, question: str) -> Dict[str, Any]:
        """Query the RAG system with a question."""
        try:
            # Get the answer from the chain
            answer = self.qa_chain.invoke(question)
            
            # Retrieve source documents separately
            retriever = self.vector_store.vectorstore.as_retriever(search_kwargs={"k": 4})
            source_docs = retriever.invoke(question)
            sources = [
                {
                    "content": doc.page_content[:200] + "...",
                    "metadata": doc.metadata
                }
                for doc in source_docs
            ]
            
            return {
                "answer": answer,
                "sources": sources,
                "status": "success"
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": [],
                "status": "error"
            }
    
    def clear_database(self) -> None:
        """Clear all documents from the vector store."""
        self.vector_store.delete_collection()
        # Reinitialize the vector store
        self.vector_store = VectorStore(self.config, self.embedding_manager)
        self.qa_chain = self._create_qa_chain()
    
    def get_document_count(self) -> int:
        """Get the number of documents in the vector store."""
        return self.vector_store.get_collection_count()
