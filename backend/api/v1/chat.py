import json

from backend.ai_router.router import router as ai_router
from backend.ai_router.token_counter import token_counter
from backend.database.session import get_db
from backend.providers.base_provider import Message
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    provider: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = 1024
    stream: bool = False


class ChatCompletionResponse(BaseModel):
    id: str
    model: str
    content: str
    finish_reason: str | None = None
    usage: dict | None = None


@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatCompletionResponse:
    from backend.dependencies import get_current_active_user
    user = await get_current_active_user(db=db)

    messages = [Message(role=m.role, content=m.content) for m in request.messages]

    try:
        response = await ai_router.complete(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI request failed: {str(e)}",
        )

    if response.usage:
        token_counter.record(
            provider=request.provider or "auto",
            model=response.model,
            usage=response.usage,
            user_id=str(user.id),
        )

    return ChatCompletionResponse(
        id=response.id,
        model=response.model,
        content=response.content,
        finish_reason=response.finish_reason,
        usage={
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "estimated_cost": response.usage.estimated_cost,
        } if response.usage else None,
    )


@router.post("/stream")
async def chat_stream(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.dependencies import get_current_active_user
    await get_current_active_user(db=db)

    messages = [Message(role=m.role, content=m.content) for m in request.messages]

    async def generate():
        try:
            async for chunk in ai_router.stream(
                messages=messages,
                model=request.model,
                provider=request.provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ):
                data = json.dumps({
                    "id": chunk.id,
                    "model": chunk.model,
                    "delta": chunk.delta,
                    "finish_reason": chunk.finish_reason,
                })
                yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            error_data = json.dumps({"error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
