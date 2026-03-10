"""Routes for chat conversation management."""

from datetime import datetime
from typing import List, Optional
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_database

router = APIRouter()


class ChatMessageModel(BaseModel):
    role: str
    content: str
    timestamp: Optional[str] = None


class ConversationCreate(BaseModel):
    title: Optional[str] = None
    messages: Optional[List[ChatMessageModel]] = None


class ConversationUpdate(BaseModel):
    title: Optional[str] = None


class MessagesUpdate(BaseModel):
    messages: List[ChatMessageModel]


def serialize_conversation(doc: dict, include_messages: bool = False) -> dict:
    result = {
        "id": str(doc["_id"]),
        "title": doc.get("title", "New conversation"),
        "message_count": len(doc.get("messages", [])),
        "created_at": doc.get("created_at", datetime.utcnow()).isoformat(),
        "updated_at": doc.get("updated_at", datetime.utcnow()).isoformat(),
    }
    if include_messages:
        result["messages"] = doc.get("messages", [])
    return result


@router.get("/conversations")
async def list_conversations():
    """List all conversations, newest first."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    cursor = (
        db["chat_conversations"]
        .find({}, {"messages": 0})
        .sort("updated_at", -1)
    )
    docs = await cursor.to_list(length=200)

    results = []
    for doc in docs:
        results.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", "New conversation"),
            "message_count": doc.get("message_count", 0),
            "created_at": doc.get("created_at", datetime.utcnow()).isoformat(),
            "updated_at": doc.get("updated_at", datetime.utcnow()).isoformat(),
        })
    return results


@router.post("/conversations")
async def create_conversation(body: ConversationCreate):
    """Create a new conversation."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    now = datetime.utcnow()
    messages = []
    if body.messages:
        messages = [m.model_dump() for m in body.messages]

    title = body.title
    if not title and messages:
        first_user = next((m for m in messages if m["role"] == "user"), None)
        if first_user:
            title = first_user["content"][:60].strip()
            if len(first_user["content"]) > 60:
                title += "…"
    if not title:
        title = "New conversation"

    doc = {
        "title": title,
        "messages": messages,
        "message_count": len(messages),
        "created_at": now,
        "updated_at": now,
    }

    result = await db["chat_conversations"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_conversation(doc, include_messages=True)


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a conversation with all messages."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        obj_id = ObjectId(conversation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    doc = await db["chat_conversations"].find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return serialize_conversation(doc, include_messages=True)


@router.patch("/conversations/{conversation_id}")
async def update_conversation(conversation_id: str, body: ConversationUpdate):
    """Update conversation title."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        obj_id = ObjectId(conversation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    update_data: dict = {"updated_at": datetime.utcnow()}
    if body.title is not None:
        update_data["title"] = body.title

    result = await db["chat_conversations"].find_one_and_update(
        {"_id": obj_id}, {"$set": update_data}, return_document=True
    )
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return serialize_conversation(result, include_messages=False)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        obj_id = ObjectId(conversation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    result = await db["chat_conversations"].delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"message": "Conversation deleted"}


@router.put("/conversations/{conversation_id}/messages")
async def save_messages(conversation_id: str, body: MessagesUpdate):
    """Save/replace all messages in a conversation. Also updates title from first user message if title is still default."""
    db = get_database()
    if db is None:
        raise HTTPException(status_code=503, detail="Database not available")

    try:
        obj_id = ObjectId(conversation_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")

    messages = [m.model_dump() for m in body.messages]

    doc = await db["chat_conversations"].find_one({"_id": obj_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Conversation not found")

    update_data: dict = {
        "messages": messages,
        "message_count": len(messages),
        "updated_at": datetime.utcnow(),
    }

    # Auto-generate title from first user message if it's still the default
    if doc.get("title") in ("New conversation", None, ""):
        first_user = next((m for m in messages if m["role"] == "user"), None)
        if first_user:
            content = first_user["content"]
            title = content[:60].strip()
            if len(content) > 60:
                title += "…"
            update_data["title"] = title

    result = await db["chat_conversations"].find_one_and_update(
        {"_id": obj_id}, {"$set": update_data}, return_document=True
    )

    return serialize_conversation(result, include_messages=True)
