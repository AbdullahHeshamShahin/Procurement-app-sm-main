"""Routes for AI chat assistant."""

from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.services.chat_service import ChatService

router = APIRouter()
chat_service = ChatService()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


@router.post("/chat")
async def chat(request: ChatRequest):
    """Stream an AI chat response with full procurement system context."""
    if not chat_service.is_available():
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Please configure OPENAI_API_KEY.",
        )

    if not request.messages:
        raise HTTPException(status_code=400, detail="No messages provided")

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_stream():
        async for chunk in chat_service.stream_chat(messages):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
