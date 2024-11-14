from fastapi import FastAPI, HTTPException
#from pydantic import BaseModel
from transformers import pipeline
import logging
#from typing import Optional, List
from shared.models import summary_req

# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

#this loads the summarization model and checks if there is an error in loading the model
logger.info("Loading the summarization model ...")
try:
    summarizer = pipeline("summarization", model = "Falconsai/text_summarization")
    logger.info("Model has been successfully loaded.")
except Exception as e:
    logger.error(f"Model failed to load. excption is {e}")
    raise


#class summary_req(BaseModel):  #this handles the incoming request
    
    text: Optional[str] = None
    texts: Optional[List[str]] = None
    max_length: Optional[int] = 1000
    min_length: Optional[int] = 30


@app.post("/summarize/")
async def summarize(request: summary_req):
    logger.info(f"summarization request received, of length: single_text={bool(request.text)}, multi_texts={bool(request.texts)}")

    if request.text:
        # if there is only single text to summarize
        logger.info(f"summarization request received, of length: {len(request.text)}")
        summary = summarizer(request.text, max_length=request.max_length, min_length=request.min_length)
        return {"summary": summary[0]['summary_text']}
    elif request.texts:
        # if multiple texts are provided 
        logger.info(f"summarization request received, batch size: {len(request.texts)}")
        summaries = [summarizer(text, max_length=request.max_length, min_length=request.min_length)[0]['summary_text'] for text in request.texts]
        return {"summaries": summaries}
    else:
        # If neither 'text' nor 'texts' is provided
        logger.warning("No valid input provided can be summarized")
        raise HTTPException(status_code=400, detail =" no valid input provided")
    