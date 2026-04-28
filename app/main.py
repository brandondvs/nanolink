import random, string
from datetime import datetime, timezone

from app.database.model import Link, LinkEvent
from app.settings import Config

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from sqlmodel import SQLModel, create_engine, Session, select
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

config = Config()

engine = create_engine(config.database_url, echo=config.debug)


class CreateLink(BaseModel):
    url: HttpUrl
    expires_at: datetime


SQLModel.metadata.create_all(engine)


def generate_code(length=6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


@app.post("/create")
async def create_link(create_link: CreateLink):
    with Session(engine) as session:
        while True:
            code = generate_code()
            existing = session.exec(select(Link).where(Link.code == code)).first()
            if not existing:
                break

        link = Link(
            url=str(create_link.url), code=code, expires_at=create_link.expires_at
        )
        session.add(link)
        session.commit()
        return {"code": code, "link": link.url, "expires_at": link.expires_at}


@app.get("/{slug}")
async def get_link(slug: str, debug: bool = False):
    with Session(engine) as session:
        statement = select(Link).where(Link.code == slug)
        link = session.exec(statement).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

        if link.expires_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="Link expired")

        session.add(LinkEvent(link_id=link.id))
        session.commit()
        session.refresh(link)

        if debug:
            return {"link": link.url, "redirect": False, "debug": debug}

        return RedirectResponse(url=link.url, status_code=307)


@app.get("/metrics/{slug}")
async def get_metrics(slug: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.code == slug)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        return {
            "code": link.code,
            "url": link.url,
            "total_clicks": len(link.events),
            "events": link.events,
            "expires_at": link.expires_at,
        }


@app.delete("/delete/{slug}")
async def delete_link(slug: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.code == slug)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        session.delete(link)
        session.commit()
        return {"deleted": slug}
