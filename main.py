import random, string

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, create_engine, Session, select

from model import Link, LinkEvent

app = FastAPI()


class Settings(BaseSettings):
    database_url: str = ""
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(settings.database_url, echo=settings.debug)


class CreateLink(BaseModel):
    url: HttpUrl


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

        link = Link(url=str(create_link.url), code=code)
        session.add(link)
        session.commit()
        return {"code": code, "link": link.url}


@app.get("/{slug}")
async def get_link(slug: str, debug: bool = False):
    with Session(engine) as session:
        statement = select(Link).where(Link.code == slug)
        link = session.exec(statement).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")

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
