from fastapi import FastAPI

app = FastAPI(title="NSGates API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "FastAPI rodando junto com Django!"}

@app.get("/status")
def status():
    return {"status": "online"}
