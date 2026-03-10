"""PDF and document text extraction service."""
import io
from typing import Optional
import PyPDF2


class PDFService:
    """Service for extracting text from PDF documents."""

    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text content from a PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_parts = []

            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    # If a page fails, continue with other pages
                    text_parts.append(f"\n[Error extracting page {page_num + 1}: {str(e)}]\n")

            return "\n\n".join(text_parts) if text_parts else ""
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")

    @staticmethod
    def extract_text_from_file(file_content: bytes, file_type: str) -> str:
        """Extract text from various file types."""
        if file_type == "application/pdf" or file_type.endswith("pdf"):
            return PDFService.extract_text_from_pdf(file_content)
        elif file_type in ["text/plain", "text/txt"] or file_type.endswith("txt"):
            # For text files, decode directly
            try:
                return file_content.decode("utf-8", errors="ignore")
            except Exception as e:
                raise ValueError(f"Failed to decode text file: {str(e)}")
        else:
            # For other file types, try to decode as text
            try:
                return file_content.decode("utf-8", errors="ignore")
            except Exception as e:
                raise ValueError(
                    f"Unsupported file type: {file_type}. Only PDF and TXT files are supported."
                )

