from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel

app = FastAPI()

class summaryRequest(BaseModel):
    text: str

@app.post("/summarize/")
def summarize(request: summaryRequest):
    try:
        response = requests.post("http://summarize_service:8001/summarize/", json=request.dict())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))