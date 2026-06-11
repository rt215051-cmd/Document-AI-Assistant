# PDF AI Agent

A complete RAG (Retrieval-Augmented Generation) application for querying PDF documents using local LLMs via Ollama.

## Features

- **PDF Processing**: Extract text and tables from PDF files using PyPDF2 and pdfplumber
- **Text Chunking**: Intelligent text splitting with LangChain's RecursiveCharacterTextSplitter
- **Vector Embeddings**: Generate embeddings using sentence-transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for efficient similarity search
- **RAG System**: Question-answering with context retrieval using LangChain
- **Chat Interface**: Modern Streamlit UI for interactive conversations
- **Local LLM**: Uses Ollama for self-hosted, free inference (no API keys required)

## Tech Stack

- **PDF Processing**: PyPDF2, pdfplumber
- **Text Chunking**: LangChain (RecursiveCharacterTextSplitter)
- **Embeddings**: sentence-transformers
- **Vector DB**: ChromaDB
- **LLM**: Ollama (self-hosted)
- **Framework**: LangChain
- **UI**: Streamlit

## Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running
   - Download from: https://ollama.ai/download
   - Install a model (e.g., `ollama pull llama2`)
   - Start Ollama server: `ollama serve`

## Installation

1. Clone or navigate to the project directory:
```bash
cd "c:/Users/user/Desktop/pdf ai agent"
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy the environment configuration:
```bash
copy .env.example .env  # On Windows
# cp .env.example .env  # On Linux/Mac
```

5. (Optional) Edit `.env` to customize settings:
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Usage

1. Start Ollama (if not already running):
```bash
ollama serve
```

2. Run the Streamlit application:
```bash
streamlit run app.py
```

3. Open your browser to the URL shown (usually `http://localhost:8501`)

4. **Upload a PDF** using the sidebar file uploader

5. **Ask questions** about your PDF content in the chat interface

## Project Structure

```
pdf ai agent/
├── app.py                 # Streamlit chat interface
├── config.py              # Configuration management
├── pdf_processor.py       # PDF text and table extraction
├── embedding_manager.py   # Text chunking and embeddings
├── vector_store.py        # ChromaDB vector store management
├── rag_system.py          # RAG system with LangChain
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── .env                  # Your environment configuration (create this)
└── chroma_db/            # ChromaDB persistent storage (auto-created)
```

## How It Works

1. **PDF Upload**: User uploads a PDF file through the Streamlit interface
2. **Text Extraction**: PDF is processed using pdfplumber to extract text and tables
3. **Text Chunking**: Long text is split into manageable chunks (1000 chars by default)
4. **Embedding Generation**: Each chunk is converted to a vector embedding
5. **Vector Storage**: Embeddings are stored in ChromaDB for fast similarity search
6. **Query Processing**: When a user asks a question:
   - The question is embedded
   - Similar chunks are retrieved from ChromaDB
   - Retrieved chunks are used as context for the LLM
   - Ollama generates an answer based on the context
7. **Response Display**: Answer is shown with source document references

## Configuration Options

Edit `.env` to customize:

- `OLLAMA_BASE_URL`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Ollama model to use (default: `llama2`)
- `CHROMA_PERSIST_DIRECTORY`: Where ChromaDB stores data (default: `./chroma_db`)
- `CHROMA_COLLECTION_NAME`: Name of the vector collection (default: `pdf_documents`)
- `CHUNK_SIZE`: Text chunk size in characters (default: `1000`)
- `CHUNK_OVERLAP`: Overlap between chunks (default: `200`)
- `EMBEDDING_MODEL`: Sentence transformer model (default: `all-MiniLM-L6-v2`)

## Troubleshooting

**Ollama connection error:**
- Ensure Ollama is running: `ollama serve`
- Check the URL in `.env` matches your Ollama server

**Model not found:**
- Pull the model: `ollama pull llama2` (or your chosen model)
- Update `OLLAMA_MODEL` in `.env`

**Memory issues:**
- Reduce `CHUNK_SIZE` in `.env`
- Use a smaller Ollama model (e.g., `phi` instead of `llama2`)

**Slow response times:**
- First query is slower (embeddings need to be generated)
- Subsequent queries are faster
- Consider using a GPU for Ollama if available

## License

MIT License - Feel free to use and modify as needed.
