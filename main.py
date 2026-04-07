import random, string

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
from sqlmodel import SQLModel, create_engine, Session, select

from model import Link, LinkEvent

app = FastAPI()


class Settings(BaseSettings):
    database_url: str = ""

    class Config:
        env_file = ".env"


settings = Settings()

engine = create_engine(settings.database_url, echo=True)


class CreateLink(BaseModel):
    data: HttpUrl


SQLModel.metadata.create_all(engine)


def generate_code(length=6) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


@app.post("/create")
async def create_link(createLink: CreateLink):
    code = generate_code()
    link = Link(url=str(createLink.data), code=code)
    with Session(engine) as session:
        session.add(link)
        session.commit()
    return {"code": code}


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
        return link


@app.delete("/delete/{slug}")
async def delete_link(slug: str):
    with Session(engine) as session:
        link = session.exec(select(Link).where(Link.code == slug)).first()
        if not link:
            raise HTTPException(status_code=404, detail="Link not found")
        session.delete(link)
        session.commit()
        return {"deleted": slug}
