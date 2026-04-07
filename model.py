from sqlmodel import SQLModel, Field


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    code: str = Field(index=True, unique=True)
