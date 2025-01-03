from pydantic import BaseModel, constr, Field
from datetime import date
from app.db.schemas.issues import Issues


class Repositories(BaseModel):
    name: str  # type: ignore
    id: int
    is_visible: bool
    issues_count: int
    issues: list[Issues] = []

    class Config:
        orm_mode = True


class RepositoriesCreate(Repositories):
    name: str = Field(max_length=50)
