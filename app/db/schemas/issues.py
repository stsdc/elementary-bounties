from pydantic import BaseModel, Field


class Issues(BaseModel):
    title: str
    state: bool
    number: int
    cumulative_bounty: int
    repository_id: int
    url: str

    class Config:
        from_attributes = True


class IssuesCreate(Issues):
    title: str = Field(max=200)
