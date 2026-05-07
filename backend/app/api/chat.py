from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.schemas import ChatRequest, ChatResponse
from app.core.rag_engine import RAGEngine
from app.db.chat_store import (
    create_conversation,
    save_message,
    get_conversations,
    get_conversation_messages,
    delete_conversation,
)

router = APIRouter()
engine = RAGEngine()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        is_new = request.conversation_id is None
        conv_id = request.conversation_id

        if is_new:
            title = request.query[:80]
            conv_id = await create_conversation(title)

        history_rows = await get_conversation_messages(conv_id) if not is_new else []
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in history_rows
        ]

        result = engine.chat(
            query=request.query,
            conversation_id=conv_id,
            top_k=request.top_k,
            history=history,
        )

        await save_message(conv_id, "user", request.query)
        await save_message(conv_id, "assistant", result["answer"], result["sources"])

        return ChatResponse(
            query=request.query,
            answer=result["answer"],
            sources=result["sources"],
            conversation_id=conv_id,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/conversations")
async def list_conversations():
    return await get_conversations()


@router.get("/conversations/{conversation_id}/messages")
async def get_messages(conversation_id: str):
    messages = await get_conversation_messages(conversation_id)
    return {"conversation_id": conversation_id, "messages": messages}


@router.delete("/conversations/{conversation_id}")
async def remove_conversation(conversation_id: str):
    await delete_conversation(conversation_id)
    return {"message": "Conversation deleted"}
