from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.rule_core import parse_goal
from app.services.openclaw_worker import execute_openclaw_skill

app = FastAPI(title="AutoFabric Starter API", version="0.1.0")


class GoalRequest(BaseModel):
    raw_input: str


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}


@app.post("/goals/parse")
def goals_parse(payload: GoalRequest):
    return parse_goal(payload.raw_input)


@app.post("/openclaw/test")
def openclaw_test():
    return execute_openclaw_skill("ping", {"message": "hello from autofabric"})
