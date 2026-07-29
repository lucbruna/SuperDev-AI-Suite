from pydantic import BaseModel, Field


class SandboxLimits(BaseModel):
    max_cpu: float = Field(default=1.0, ge=0.1, le=128.0, description="Max CPU cores")
    max_memory: int = Field(default=512, ge=16, description="Max memory in MB")
    max_disk: int = Field(default=1024, ge=1, description="Max disk in MB")
    max_processes: int = Field(default=50, ge=1, description="Max number of processes")
    max_time: int = Field(default=30, ge=1, description="Max execution time in seconds")
