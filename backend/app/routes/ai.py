"""Routes for AI-powered features."""
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.metadata import (
    DocumentExtractionResponse,
    CommodityGroupSuggestion,
    TextExtractionResponse,
)
from app.services.ai_service import AIService
from app.services.pdf_service import PDFService

router = APIRouter()
ai_service = AIService()
pdf_service = PDFService()


@router.post("/extract-text", response_model=TextExtractionResponse)
async def extract_text(file: UploadFile = File(...)):
    """Extract raw text from an uploaded document (PDF, TXT, etc.)."""
    try:
        content = await file.read()
        file_type = file.content_type or "application/octet-stream"
        text = pdf_service.extract_text_from_file(content, file_type)

        return TextExtractionResponse(
            text=text,
            file_name=file.filename or "unknown",
            file_type=file_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Text extraction failed: {str(e)}"
        )


@router.post("/extract-document", response_model=DocumentExtractionResponse)
async def extract_document(file: UploadFile = File(...)):
    """Extract information from an uploaded vendor offer document using AI."""
    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.",
        )

    # Read file content and extract text
    content = await file.read()
    file_type = file.content_type or "application/octet-stream"
    
    try:
        # Extract text from PDF or other formats
        text_content = pdf_service.extract_text_from_file(content, file_type)
    except ValueError:
        # Fallback to UTF-8 decoding for text files
        text_content = content.decode("utf-8", errors="ignore")

    try:
        return await ai_service.extract_document(text_content)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Document extraction failed: {str(e)}"
        )


@router.post("/suggest-commodity-group", response_model=CommodityGroupSuggestion)
async def suggest_commodity_group(
    title: str = Form(...), order_lines_json: str = Form(...)
):
    """Suggest the best commodity group based on request title and order lines using AI."""
    if not ai_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="OpenAI client not initialized. Please set OPENAI_API_KEY environment variable.",
        )

    try:
        order_lines = json.loads(order_lines_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid order lines JSON")

    try:
        return await ai_service.suggest_commodity_group(title, order_lines)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Commodity group suggestion failed: {str(e)}"
        )

