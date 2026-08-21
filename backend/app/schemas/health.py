from pydantic import BaseModel, Field
from datetime import datetime


class LivenessResponse(BaseModel):
    status: str = Field(default="healthy", description="Application liveness status")
    version: str = Field(description="Application version")
    timestamp: str = Field(description="ISO timestamp")


class ReadinessResponse(BaseModel):
    status: str = Field(description="Readiness status ('ready' or 'unhealthy')")
    database_connected: bool = Field(description="PostgreSQL connectivity status")
    version: str = Field(description="Application version")
    timestamp: str = Field(description="ISO timestamp")
