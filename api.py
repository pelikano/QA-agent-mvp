from fastapi import FastAPI
from core.agent import run_agent

app = FastAPI()

@app.post("/analyze")
def analyze_story(story: dict):
    return run_agent(story)
