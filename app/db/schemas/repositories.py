"""Repositories schemas."""
from pydantic import BaseModel, Field
from app.db.schemas.issues import Issues


class Repositories(BaseModel):
    name: str
    description: str | None
    id: int
    is_visible: bool
    issues_count: int
    issues: list[Issues] = []

    class Config:
        from_attributes = True


class RepositoriesCreate(Repositories):
    name: str = Field(max_length=50)
    description: str | None = Field(max_length=250)
