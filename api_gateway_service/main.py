from fastapi import FastAPI, Query, HTTPException
import requests
#from pydantic import BaseModel
import logging
import httpx
from typing import List, Optional
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
async def summarize_and_store(request: summary_req, return_text: Optional[bool] = Query(False)):  #this handles the incoming request
    logger.info(f"API request with text: {bool(request.text)} and texts: {bool(request.texts)}")

    if not request.text and not request.texts:
        logger.warning("Input is empty. no text has beeen provided")
        raise HTTPException(status_code=400, detail="Text input cannot be empty.")
    
    try:    
        if request.text:
          texts = [request.text]
        else:
         texts = request.texts

        try:
       
            logger.info("Request sent to the summarize service")
            async with httpx.AsyncClient() as client:

                response = await client.post("http://summarize_service:8001/summarize/", json=request.dict())
                response.raise_for_status()
            
                response_json = response.json()
                if "summary" in response_json:  # Single text
                    summaries = [response_json["summary"]]
                elif "summaries" in response_json:  # Batch texts
                    summaries = response_json["summaries"]
                else:
                    raise HTTPException(status_code=500, detail="Unexpected response from summarize service")
                logger.info(f"Request payload: {request.dict()}")
                logger.info(f"Summarize service response: {response.json()}")

        except httpx.HTTPError as e:
            logger.info(f"error in connecting to summarize_service: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error connecting to summarization service: {str(e)}")
   
        paired_data = [{"original_text": text, "summarized_text": summary} for text, summary in zip(texts, summaries)]
        logger.info("Sending summarized data to storage service.")
        
        try:    
            async with httpx.AsyncClient() as client:

                if len(paired_data) == 1:
                    data_to_store = paired_data[0]  # Single Summary object
                else:
                    data_to_store = {"Summaries": paired_data}  # Batchsummary object

                store_response = await client.post(
                    "http://storage_service:8002/store/",
                    json=data_to_store  # Send as a batch
                )

                store_response.raise_for_status()

        except httpx.HTTPError as e:
            logger.error(f"Error from storage service: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Storage service error: {str(e)}"
                )  
        if return_text:
            result = paired_data  # this includes the original text and summary
        else:
            result = summaries    # only the summary

        logger.info("Summarization and storage successfully processed.")
        return {"message": "summaries sucessfully processed and stored.", "result": result}
    
    except Exception as e:
        logger.info(f"unexpexted error, this might be from the services: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    