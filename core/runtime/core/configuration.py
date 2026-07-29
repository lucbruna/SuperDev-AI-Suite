from pydantic_settings import BaseSettings
from pydantic import Field



class RuntimeConfig(BaseSettings):
    default_timeout: int = Field(default=30, ge=1, description="Default execution timeout in seconds")
    max_memory: int = Field(default=512, ge=64, description="Max memory per session in MB")
    max_cpu: float = Field(default=1.0, ge=0.1, le=128.0, description="Max CPU cores per session")
    sandbox_enabled: bool = Field(default=True, description="Enable sandboxed execution")
    docker_enabled: bool = Field(default=False, description="Enable Docker-based execution")
    allowed_languages: list[str] = Field(default=["python", "node", "shell"], description="Allowed runtime languages")

    model_config = {"env_prefix": "SUPERDEV_RUNTIME_"}
