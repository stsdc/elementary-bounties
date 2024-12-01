from pydantic import BaseModel, constr, Field
from datetime import date
from app.db.schemas.posts import Posts


class Issues(BaseModel):
    title: str
    completed: bool
    issue_number: int
    cumulative_bounty: int
    repository_id: int

    class Config:
        orm_mode = True


class IssuesCreate(Issues):
    title: str = Field(max=200)
