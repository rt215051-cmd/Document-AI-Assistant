# Snowflake Deployment Guide for PDF AI Agent

## Overview

This guide explains how to deploy the PDF AI Agent to Snowflake. There are three main deployment options:

1. **Streamlit in Snowflake (SiS)** - Run as a native object in Snowflake
2. **Snowflake Native Apps** - Package app with data and share with other Snowflake accounts
3. **Snowpark Container Services** - Deploy in a container optimized for Snowflake

## Required Modifications for Snowflake Compatibility

### Current Architecture Challenges

The current PDF AI Agent uses components that are not compatible with Snowflake's environment:

1. **Ollama LLM (Local)** - Requires external LLM service
2. **ChromaDB (Local Vector Store)** - Requires Snowflake-compatible vector storage
3. **Sentence Transformers (Local Embeddings)** - May need alternative approach
4. **Local File Processing** - Needs adaptation for Snowflake's environment

### Recommended Architecture Changes

#### Option 1: Streamlit in Snowflake (Recommended for Internal Use)

**Changes Required:**

1. **Replace Ollama with Snowflake Cortex or External API**
   - Use Snowflake Cortex for LLM capabilities
   - Or use external API (OpenAI, Anthropic, etc.)

2. **Replace ChromaDB with Snowflake Vector Storage**
   - Use Snowflake's VECTOR data type and similarity search
   - Or use external vector database (Pinecone, Weaviate)

3. **Adapt File Processing**
   - Use Snowflake stages for file storage
   - Process files within Snowflake environment

#### Option 2: Snowpark Container Services (Most Flexible)

**Changes Required:**

1. **Containerize the Application**
   - Create Dockerfile with all dependencies
   - Include Ollama or use external LLM API
   - Include ChromaDB or use external vector database

2. **Use Snowflake Compute Pool**
   - Requires enterprise account
   - Not available in trial accounts

#### Option 3: Snowflake Native Apps (For Sharing)

**Changes Required:**

1. **Package Application**
   - Create app package with all dependencies
   - Include data and configuration
   - Use Snowflake-compatible components

## Deployment Steps

### Option 1: Streamlit in Snowflake (SiS)

#### Prerequisites
- Snowflake account with appropriate permissions
- Streamlit in Snowflake enabled
- Snowflake warehouse or container runtime

#### Step 1: Modify Configuration for Snowflake

Create a new configuration file `config_snowflake.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

class SnowflakeConfig:
    # Snowflake Cortex Configuration
    SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
    SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
    SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
    
    # LLM Configuration (using Snowflake Cortex)
    LLM_MODEL = os.getenv("LLM_MODEL", "snowflake-arctic")
    
    # Vector Storage Configuration
    VECTOR_TABLE = os.getenv("VECTOR_TABLE", "pdf_embeddings")
    
    # Text Chunking Configuration
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    
    # Stage Configuration
    PDF_STAGE = os.getenv("PDF_STAGE", "@pdf_files")
```

#### Step 2: Create Snowflake-Compatible RAG System

Create `rag_system_snowflake.py` with Snowflake-specific implementations:

```python
import snowflake.connector
from snowflake.cortex import Complete
from snowflake.snowpark import Session
from snowflake.snowpark.functions import *
from typing import List, Dict, Any

class SnowflakeRAGSystem:
    def __init__(self, config: SnowflakeConfig):
        self.config = config
        self.session = self._create_snowflake_session()
        
    def _create_snowflake_session(self):
        return Session.builder.configs({
            "account": self.config.SNOWFLAKE_ACCOUNT,
            "user": self.config.SNOWFLAKE_USER,
            "password": self.config.SNOWFLAKE_PASSWORD,
            "warehouse": self.config.SNOWFLAKE_WAREHOUSE,
            "database": self.config.SNOWFLAKE_DATABASE,
            "schema": self.config.SNOWFLAKE_SCHEMA
        }).create()
    
    def ingest_pdf(self, file_path: str) -> Dict[str, Any]:
        # Upload to Snowflake stage
        # Process using Snowflake functions
        # Store embeddings in VECTOR column
        pass
    
    def query(self, question: str) -> Dict[str, Any]:
        # Use Snowflake Cortex for LLM
        # Use VECTOR similarity search
        pass
```

#### Step 3: Deploy to Snowflake

1. **Create Streamlit in Snowflake:**
   ```sql
   CREATE STREAMLIT pdf_ai_agent
   FROM '@my_stage'
   MAIN_FILE = 'app_snowflake.py'
   QUERY_TAG = 'pdf_ai_agent';
   ```

2. **Set up dependencies in environment.yml:**
   ```yaml
   name: pdf_ai_agent
   channels:
     - conda-forge
   dependencies:
     - python=3.9
     - streamlit
     - snowflake-connector-python
     - snowflake-snowpark-python
     - PyPDF2
   ```

3. **Upload files to Snowflake stage:**
   ```sql
   PUT file://app_snowflake.py @my_stage;
   PUT file://requirements_snowflake.txt @my_stage;
   ```

### Option 2: Snowpark Container Services

#### Prerequisites
- Snowflake enterprise account
- Compute pool configured
- Docker knowledge

#### Step 1: Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### Step 2: Build and Push Image

```bash
docker build -t pdf-ai-agent:latest .
docker tag pdf-ai-agent:latest <your-registry>/pdf-ai-agent:latest
docker push <your-registry>/pdf-ai-agent:latest
```

#### Step 3: Deploy to Snowflake

```sql
CREATE IMAGE REPOSITORY pdf_ai_agent_repo;
CREATE SERVICE pdf_ai_agent
  IN COMPUTE_POOL my_compute_pool
  FROM IMAGE REPOSITORY pdf_ai_agent_repo
  MIN_INSTANCES = 1
  MAX_INSTANCES = 2
  AUTO_RESUME = true;
```

### Option 3: Snowflake Native Apps

#### Step 1: Create Application Package

```sql
CREATE APPLICATION PACKAGE pdf_ai_agent_package;
```

#### Step 2: Add Streamlit App

```sql
ALTER APPLICATION PACKAGE pdf_ai_agent_package
  ADD STREAMLIT pdf_ai_streamlit
  FROM '@app_stage'
  MAIN_FILE = 'app.py';
```

#### Step 3: Create Version and Release

```sql
CREATE APPLICATION VERSION v1_0 
  FROM APPLICATION PACKAGE pdf_ai_agent_package
  USING '@app_stage';

CREATE APPLICATION pdf_ai_app
  FROM APPLICATION PACKAGE pdf_ai_agent_package
  USING VERSION v1_0;
```

## Environment Variables

Create `.env.snowflake`:

```env
# Snowflake Connection
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=your_schema

# LLM Configuration
LLM_MODEL=snowflake-arctic

# Vector Storage
VECTOR_TABLE=pdf_embeddings

# Stage Configuration
PDF_STAGE=@pdf_files
```

## Requirements for Snowflake

Create `requirements_snowflake.txt`:

```
streamlit==1.31.0
snowflake-connector-python==3.6.0
snowflake-snowpark-python==1.11.0
PyPDF2==3.0.1
python-dotenv==1.0.0
```

## Testing Locally

Before deploying to Snowflake, test with Snowflake connection locally:

```python
import streamlit as st
from rag_system_snowflake import SnowflakeRAGSystem
from config_snowflake import SnowflakeConfig

def main():
    config = SnowflakeConfig()
    rag_system = SnowflakeRAGSystem(config)
    
    # Rest of your Streamlit app
```

## Cost Considerations

- **Streamlit in Snowflake**: Uses warehouse compute credits
- **Snowpark Container Services**: Requires compute pool (enterprise only)
- **Native Apps**: Sharing costs depend on data transfer

## Security Best Practices

1. Use Snowflake's role-based access control (RBAC)
2. Store credentials in Snowflake secrets or environment variables
3. Use network policies for external access
4. Enable audit logging
5. Use encryption for sensitive data

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are in environment.yml
2. **Connection Issues**: Verify Snowflake credentials and network access
3. **Performance**: Optimize chunk size and vector search parameters
4. **Memory Issues**: Adjust warehouse size or container resources

### Debug Mode

Enable debug mode in Streamlit:
```python
import streamlit as st
st.set_option('logger.level', 'debug')
```

## Additional Resources

- [Streamlit in Snowflake Documentation](https://docs.snowflake.com/developer-guide/streamlit/about-streamlit)
- [Snowpark Container Services](https://docs.snowflake.com/developer-guide/snowpark-container-services/overview)
- [Snowflake Native Apps](https://docs.snowflake.com/developer-guide/native-apps/overview)
- [Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)

## Summary

For most use cases, **Streamlit in Snowflake (SiS)** is the recommended approach for internal deployment. It provides:
- Easy deployment
- Native Snowflake integration
- RBAC security
- No additional infrastructure management

For external sharing or complex dependencies, consider **Snowpark Container Services** or **Native Apps**.
