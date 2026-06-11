import streamlit as st
from rag_system import RAGSystem
from config import Config
import os


def initialize_session_state():
    """Initialize Streamlit session state."""
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = RAGSystem()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "document_count" not in st.session_state:
        st.session_state.document_count = 0


def main():
    st.set_page_config(
        page_title="PDF AI Agent",
        page_icon="📄",
        layout="wide"
    )
    
    initialize_session_state()
    
    st.title("📄 PDF AI Agent")
    st.markdown("Upload PDF documents and ask questions about their content using RAG (Retrieval-Augmented Generation).")
    
    # Sidebar
    with st.sidebar:
        st.header("📚 Document Management")
        
        # PDF Upload
        uploaded_file = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
            help="Upload a PDF file to add to the knowledge base"
        )
        
        if uploaded_file is not None:
            # Save uploaded file temporarily
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process the PDF
            with st.spinner("Processing PDF..."):
                result = st.session_state.rag_system.ingest_pdf(temp_path)
            
            # Clean up temp file
            os.remove(temp_path)
            
            if result["status"] == "success":
                st.success(f"✅ PDF processed successfully!")
                st.info(f"Chunks added: {result['chunks_added']}")
                st.info(f"Total documents: {result['total_documents']}")
                st.session_state.document_count = result['total_documents']
            else:
                st.error("❌ Failed to process PDF")
        
        st.divider()
        
        # Database info
        st.subheader("Database Info")
        doc_count = st.session_state.rag_system.get_document_count()
        st.metric("Documents", doc_count)
        
        st.divider()
        
        # Clear database button
        if st.button("🗑️ Clear Database"):
            st.session_state.rag_system.clear_database()
            st.session_state.document_count = 0
            st.session_state.messages = []
            st.success("Database cleared!")
            st.rerun()
        
        st.divider()
        
        # Configuration info
        st.subheader("⚙️ Configuration")
        config = Config()
        st.text(f"Ollama Model: {config.OLLAMA_MODEL}")
        st.text(f"Ollama URL: {config.OLLAMA_BASE_URL}")
        st.text(f"Chunk Size: {config.CHUNK_SIZE}")
    
    # Main chat interface
    st.header("💬 Chat")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available
            if "sources" in message and message["sources"]:
                with st.expander("📖 View Sources"):
                    for i, source in enumerate(message["sources"]):
                        st.markdown(f"**Source {i+1}:**")
                        st.text(source["content"])
                        st.caption(f"Metadata: {source['metadata']}")
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your PDFs..."):
        # Check if there are documents in the database
        if st.session_state.rag_system.get_document_count() == 0:
            st.warning("⚠️ Please upload a PDF document first!")
            return
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.rag_system.query(prompt)
                
                if result["status"] == "success":
                    st.markdown(result["answer"])
                    
                    # Add assistant message to chat history with sources
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"],
                        "sources": result["sources"]
                    })
                else:
                    st.error(result["answer"])
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["answer"]
                    })


if __name__ == "__main__":
    main()
