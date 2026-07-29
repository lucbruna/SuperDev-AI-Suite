from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class Project(BaseModel):
    id: str
    name: str
    description: str = ""


class ProjectCreate(BaseModel):
    name: str
    description: str = ""


projects_db: dict[str, Project] = {}


@router.get("/")
async def list_projects():
    return {"items": list(projects_db.values()), "total": len(projects_db)}


@router.get("/{project_id}")
async def get_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    return projects_db[project_id]


@router.post("/")
async def create_project(data: ProjectCreate):
    project = Project(id=f"proj_{len(projects_db) + 1}", **data.model_dump())
    projects_db[project.id] = project
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[project_id]
    return {"deleted": True}
