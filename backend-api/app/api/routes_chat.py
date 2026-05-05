from fastapi import APIRouter, HTTPException, Query

from app.clients.rag_client import RAGClient
from app.core.config import get_settings
from app.db.sqlite import SQLiteStore
from app.schemas.chat import (
    ChatQueryRequest,
    ChatQueryResponse,
    ConversationDetail,
    ConversationSummary,
    CreateConversationRequest,
)


router = APIRouter(prefix="/chat", tags=["chat"])


def get_store() -> SQLiteStore:
    settings = get_settings()
    return SQLiteStore(settings.database_url)


@router.post("/query", response_model=ChatQueryResponse)
async def query_chat(payload: ChatQueryRequest):
    settings = get_settings()
    store = get_store()

    conversation_id = payload.conversation_id

    if payload.save_history:
        if conversation_id:
            if not store.conversation_exists(conversation_id):
                raise HTTPException(
                    status_code=404,
                    detail="Conversation not found.",
                )
        else:
            conversation = store.create_conversation()
            conversation_id = conversation["id"]

        store.rename_conversation_if_default(conversation_id, payload.query)
        store.add_message(
            conversation_id=conversation_id,
            role="user",
            content=payload.query,
        )

    rag_response = await RAGClient(settings).query(
        query=payload.query,
        top_k=payload.top_k,
    )

    answer = rag_response.get("answer", "")
    sources = rag_response.get("sources", [])
    timings_ms = rag_response.get("timings_ms")

    if payload.save_history and conversation_id:
        store.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=answer,
            sources=sources,
            timings_ms=timings_ms,
        )

    return ChatQueryResponse(
        conversation_id=conversation_id,
        answer=answer,
        sources=sources,
        retrieval_used=rag_response.get("retrieval_used", False),
        llm_model=rag_response.get("llm_model"),
        embedding_model=rag_response.get("embedding_model"),
        collection=rag_response.get("collection"),
        mode=rag_response.get("mode"),
        cloud_api_required=rag_response.get("cloud_api_required"),
        timings_ms=timings_ms,
    )


@router.post("/conversations", response_model=ConversationSummary)
async def create_conversation(payload: CreateConversationRequest):
    store = get_store()
    return store.create_conversation(title=payload.title)


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(limit: int = Query(default=50, ge=1, le=200)):
    store = get_store()
    return store.list_conversations(limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    store = get_store()
    conversation = store.get_conversation(conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return conversation


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    store = get_store()
    deleted = store.delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    return {
        "deleted": True,
        "conversation_id": conversation_id,
    }
