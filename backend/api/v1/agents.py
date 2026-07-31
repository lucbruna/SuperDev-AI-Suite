from typing import Any

from backend.agents.agent_manager import agent_manager
from backend.auth.rbac import Action, Resource, require_permission
from backend.database.session import get_db
from backend.dependencies import get_current_active_user
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(dependencies=[Depends(get_current_active_user)])


class AgentCreateRequest(BaseModel):
    name: str
    description: str = ""
    agent_type: str = "react"
    model: str | None = None
    provider: str | None = None
    max_steps: int = 10
    temperature: float = 0.7


class AgentExecuteRequest(BaseModel):
    input: str
    context: dict | None = None


class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    agent_type: str
    status: str
    tools: list[dict]


class AgentExecuteResponse(BaseModel):
    execution_id: str
    agent_id: str
    output: str
    steps: list[dict]
    tool_calls: list[dict]
    execution_time_ms: float
    error: str | None = None


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    request: AgentCreateRequest,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.CREATE)),
) -> AgentResponse:

    try:
        agent = agent_manager.create_agent(
            name=request.name,
            description=request.description,
            agent_type=request.agent_type,
            model=request.model,
            provider=request.provider,
            max_steps=request.max_steps,
            temperature=request.temperature,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    agent_dict = agent.to_dict()
    # Find the agent ID
    agent_id = ""
    for aid, a in agent_manager._agents.items():
        if a is agent:
            agent_id = aid
            break

    return AgentResponse(
        id=agent_id,
        name=agent_dict["name"],
        description=agent_dict["description"],
        agent_type=agent_dict["agent_type"],
        status=agent_dict["status"],
        tools=agent_dict["tools"],
    )


@router.get("", response_model=list[AgentResponse])
async def list_agents(
    db: AsyncSession = Depends(get_db),
) -> list[AgentResponse]:
    agents = agent_manager.list_agents()
    return [
        AgentResponse(
            id=a["id"],
            name=a["name"],
            description=a["description"],
            agent_type=a["agent_type"],
            status=a["status"],
            tools=a["tools"],
        )
        for a in agents
    ]


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> AgentResponse:
    agent = agent_manager.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )

    agent_dict = agent.to_dict()
    return AgentResponse(
        id=agent_id,
        name=agent_dict["name"],
        description=agent_dict["description"],
        agent_type=agent_dict["agent_type"],
        status=agent_dict["status"],
        tools=agent_dict["tools"],
    )


@router.post("/{agent_id}/start", response_model=AgentResponse)
async def start_agent(
    agent_id: str,
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.UPDATE)),
) -> AgentResponse:
    if not agent_manager.start_agent(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    agent = agent_manager.get_agent(agent_id)
    agent_dict = agent.to_dict()
    return AgentResponse(
        id=agent_id,
        name=agent_dict["name"],
        description=agent_dict["description"],
        agent_type=agent_dict["agent_type"],
        status=agent_dict["status"],
        tools=agent_dict["tools"],
    )


@router.post("/{agent_id}/stop", response_model=AgentResponse)
async def stop_agent(
    agent_id: str,
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.UPDATE)),
) -> AgentResponse:
    if not agent_manager.stop_agent(agent_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
    agent = agent_manager.get_agent(agent_id)
    agent_dict = agent.to_dict()
    return AgentResponse(
        id=agent_id,
        name=agent_dict["name"],
        description=agent_dict["description"],
        agent_type=agent_dict["agent_type"],
        status=agent_dict["status"],
        tools=agent_dict["tools"],
    )


@router.post("/{agent_id}/execute", response_model=AgentExecuteResponse)
async def execute_agent(
    agent_id: str,
    request: AgentExecuteRequest,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.EXECUTE)),
) -> AgentExecuteResponse:
    user = _user

    result = await agent_manager.execute_agent(
        agent_id=agent_id,
        input_text=request.input,
        context=request.context,
        user_id=str(user.id),
    )

    if "error" in result and result.get("execution_id") is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result["error"],
        )

    return AgentExecuteResponse(
        execution_id=result["execution_id"],
        agent_id=result["agent_id"],
        output=result["output"],
        steps=result["steps"],
        tool_calls=result["tool_calls"],
        execution_time_ms=result["execution_time_ms"],
        error=result.get("error"),
    )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
    _user: Any = Depends(require_permission(Resource.AGENTS, Action.DELETE)),
) -> None:

    deleted = agent_manager.delete_agent(agent_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found",
        )
