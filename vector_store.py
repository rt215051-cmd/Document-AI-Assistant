import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List, Optional
from config import Config
from embedding_manager import EmbeddingManager


class VectorStore:
    """Manage ChromaDB vector store for RAG."""
    
    def __init__(self, config: Config = None, embedding_manager: EmbeddingManager = None):
        self.config = config or Config()
        self.embedding_manager = embedding_manager or EmbeddingManager(self.config)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.config.CHROMA_PERSIST_DIRECTORY)
        
        # Custom embedding function for LangChain
        class CustomEmbeddingFunction:
            def __init__(self, embedding_manager):
                self.embedding_manager = embedding_manager
            
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return self.embedding_manager.generate_embeddings(texts)
            
            def embed_query(self, text: str) -> List[float]:
                return self.embedding_manager.generate_embedding(text)
        
        self.embedding_function = CustomEmbeddingFunction(self.embedding_manager)
        
        # Initialize vector store
        self.vectorstore = Chroma(
            client=self.client,
            collection_name=self.config.CHROMA_COLLECTION_NAME,
            embedding_function=self.embedding_function
        )
    
    def add_documents(self, documents: List[Document]) -> None:
        """Add documents to the vector store."""
        self.vectorstore.add_documents(documents)
    
    def add_texts(self, texts: List[str], metadatas: List[dict] = None) -> None:
        """Add texts to the vector store."""
        self.vectorstore.add_texts(texts, metadatas=metadatas)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents."""
        return self.vectorstore.similarity_search(query, k=k)
    
    def similarity_search_with_score(self, query: str, k: int = 4) -> List[tuple]:
        """Search for similar documents with scores."""
        return self.vectorstore.similarity_search_with_score(query, k=k)
    
    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(self.config.CHROMA_COLLECTION_NAME)
    
    def get_collection_count(self) -> int:
        """Get the number of documents in the collection."""
        return self.vectorstore._collection.count()
