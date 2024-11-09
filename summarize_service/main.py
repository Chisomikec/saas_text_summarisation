from fastapi import FastAPI, HTTPException
from pydantic import Basemodel
from transformers import pipeline
import logging


# logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

#this loads the summarization model and checks if there is an error in loading the model
logger.info("Loading the summarization model ...")
try:
    summarizer = pipeline("summerization", model = "Falconsai/text_summarization")
    logger.info("Model has been successfully loaded.")
except Exception as e:
    logger.error(f"Model failed to load. excption is {e}")
    raise


class summary_req(Basemodel):  #this handles the incoming request
    text: str
    max_len: int = 1000
    min_len: int=30  


@app.post("/summarize/")
def summarize(request: summary_req):
    logger.info(f"summarization request received, of length: {len(request.text)}")

    try:
        # this generates the summary within the specified length
        summary = summarizer(request.text,
                        max_len= request.max_len,
                        min_len= request.min_len,
                        do_sample=False)
        logger.info("summary has been successfully generated.")
        return{"summary": summary[0]["summary_text"]}
    except Exception as e:
        logger.error(f"error in generating summary: {e}")
        raise HTTPException(status_code=500, detail="An error has occured while generating the summary.") 