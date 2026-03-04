from fastapi import FastAPI

app = FastAPI(title="Outreach Agent Scaffolding")

@app.get("/")
def read_root():
    return {"status":"ok","repo":"TopEquations outreach-agent scaffold"}
