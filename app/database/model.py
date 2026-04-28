from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship


class Link(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str
    code: str = Field(index=True, unique=True)
    events: list["LinkEvent"] = Relationship(back_populates="link", cascade_delete=True)
    expires_at: datetime


class LinkEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    link_id: int | None = Field(
        default=None, foreign_key="link.id", index=True, ondelete="CASCADE"
    )
    link: Link = Relationship(back_populates="events")
