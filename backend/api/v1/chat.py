import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai_router.router import router as ai_router
from backend.agents.react_agent import ReActAgent
from backend.ai_router.token_counter import token_counter
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from backend.providers.base_provider import Message

logger = logging.getLogger(__name__)

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


class AgentChatRequest(BaseModel):
    message: str
    model: str | None = None
    provider: str | None = None
    temperature: float = 0.7
    max_steps: int = 20


class AgentChatResponse(BaseModel):
    content: str
    tool_calls: list[dict]
    error: str | None = None


@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_active_user),
) -> ChatCompletionResponse:
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Messages list cannot be empty",
        )

    messages = [Message(role=m.role, content=m.content) for m in request.messages]

    try:
        response = await ai_router.complete(
            messages=messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            db=db,
        )
    except ValueError as e:
        logger.warning(f"Validation error in chat_completions: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except ConnectionError as e:
        logger.error(f"AI provider connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service temporarily unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in chat_completions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error processing chat request",
        )

    if response.usage:
        token_counter.record(
            provider=request.provider or "auto",
            model=response.model,
            usage=response.usage,
            user_id=str(user["id"]),
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
        }
        if response.usage
        else None,
    )


@router.post("/agent", response_model=AgentChatResponse)
async def agent_chat(
    request: AgentChatRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_active_user),
) -> AgentChatResponse:
    """Run a workspace-enabled coding agent for a chat request."""
    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty",
        )

    try:
        agent = ReActAgent(
            name="Workspace Code Assistant",
            description="Autonomously inspects and changes the current project when requested.",
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_steps=max(1, min(request.max_steps, 30)),
            db=db,
        )
        result = await agent.run(request.message, context={"user_id": str(user["id"])})
        return AgentChatResponse(
            content=result.output,
            tool_calls=[
                {"name": call.name, "arguments": call.arguments, "error": call.error}
                for call in result.tool_calls
            ],
            error=result.error,
        )
    except ValueError as e:
        logger.warning(f"Validation error in agent_chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}",
        )
    except TimeoutError as e:
        logger.error(f"Agent execution timeout: {e}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Agent execution timed out",
        )
    except ConnectionError as e:
        logger.error(f"Agent connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Agent service temporarily unavailable",
        )
    except Exception as e:
        logger.exception(f"Unexpected error in agent_chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during agent execution",
        )


@router.post("/stream")
async def chat_stream(
    request: ChatCompletionRequest,
    db: AsyncSession = Depends(get_db),
    user: dict[str, Any] = Depends(get_current_active_user),
):
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Messages list cannot be empty",
        )

    messages = [Message(role=m.role, content=m.content) for m in request.messages]

    async def generate():
        try:
            async for chunk in ai_router.stream(
                messages=messages,
                model=request.model,
                provider=request.provider,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                db=db,
            ):
                data = json.dumps(
                    {
                        "id": chunk.id,
                        "model": chunk.model,
                        "delta": chunk.delta,
                        "finish_reason": chunk.finish_reason,
                    }
                )
                yield f"data: {data}\n\n"
            yield "data: [DONE]\n\n"
        except ValueError as e:
            logger.warning(f"Validation error in chat_stream: {e}")
            error_data = json.dumps({"error": f"Invalid request: {str(e)}"})
            yield f"data: {error_data}\n\n"
        except ConnectionError as e:
            logger.error(f"AI provider connection error in stream: {e}")
            error_data = json.dumps({"error": "AI service temporarily unavailable"})
            yield f"data: {error_data}\n\n"
        except Exception as e:
            logger.exception(f"Unexpected error in chat_stream: {e}")
            error_data = json.dumps({"error": "Internal server error"})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
