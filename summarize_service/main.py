from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import logging


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


class summary_req(BaseModel):  #this handles the incoming request
    text: str
    max_length: int = 1000
    min_length: int=30  


@app.post("/summarize/")
def summarize(request: summary_req):
    logger.info(f"summarization request received, of length: {len(request.text)}")

    try:
        # this generates the summary within the specified length
        summary = summarizer(request.text,
                        max_length= request.max_length,
                        min_length= request.min_length,
                        do_sample=False)
        logger.info("summary has been successfully generated.")
        return{"summary": summary[0]["summary_text"]}
    except Exception as e:
        logger.error(f"error in generating summary: {e}")
        raise HTTPException(status_code=500, detail="An error has occured while generating the summary.") 