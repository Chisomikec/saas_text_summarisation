from fastapi import FastAPI, HTTPException
import requests
#from pydantic import BaseModel
import logging
import httpx
#from typing import List, Optional
from shared.models import summary_req

app = FastAPI()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

#this defines the 
#class summaryRequest(BaseModel):
 #   text: Optional[str] = None
  #  texts: Optional[str] = None
   # text: Optional[int] = None
    #text: Optional[int] = None


@app.post("/summarize/")
async def summarize(request: summary_req):  #this handles the incoming request
    logger.info(f"API request with text: {bool(request.text)} and texts: {bool(request.texts)}")

    if not request.text and not request.texts:
        logger.warning("Input is empty. no text has beeen provided")
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    try:
       
        logger.info("Request sent to the summarize service")
        async with httpx.AsyncClient() as client:

            response = await client.post("http://summarize_service:8001/summarize/", json=request.dict())
            response.raise_for_status()
            
            return response.json()
        
    except httpx.RequestException as e:
        logger.info(f"error in connecting to summarize_service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error connecting to summarization service: {str(e)}")
    except Exception as e:
        logger.info(f"error returned by summarize service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")