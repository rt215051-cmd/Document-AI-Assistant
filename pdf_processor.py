import PyPDF2
import pdfplumber
from typing import List, Dict, Any
import io


class PDFProcessor:
    """Process PDF files to extract text and tables."""
    
    def __init__(self):
        pass
    
    def extract_text_pypdf2(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2."""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text with PyPDF2: {e}")
        return text
    
    def extract_text_pdfplumber(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error extracting text with pdfplumber: {e}")
        return text
    
    def extract_tables(self, pdf_path: str) -> List[List[List[str]]]:
        """Extract tables from PDF using pdfplumber."""
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception as e:
            print(f"Error extracting tables: {e}")
        return tables
    
    def extract_all(self, pdf_path: str) -> Dict[str, Any]:
        """Extract all content from PDF (text and tables)."""
        text = self.extract_text_pdfplumber(pdf_path)
        tables = self.extract_tables(pdf_path)
        
        # Convert tables to text format
        table_text = ""
        for i, table in enumerate(tables):
            table_text += f"\n--- Table {i+1} ---\n"
            for row in table:
                table_text += " | ".join([str(cell) if cell else "" for cell in row]) + "\n"
        
        return {
            "text": text,
            "tables": tables,
            "combined_text": text + table_text
        }
    
    def process_pdf(self, pdf_path: str) -> str:
        """Process PDF and return combined text content."""
        content = self.extract_all(pdf_path)
        return content["combined_text"]
