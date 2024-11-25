from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import logging
from pydantic import BaseModel
from typing import List, Union
from shared.models import Summary, BatchSummary

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

try:
    client = MongoClient("mongodb://root:password@mongodb:27017/")
    print(client.list_database_names())
    db = client.summarization_db
    collection = db.summary
    logger.info("mongodb connected")
except Exception as e:
    logger.error(f"Failed to connect to mongodb: {e}")
    raise

#class Summary(BaseModel):
 #   original_text: str
  #  summarized_text: str

#class BatchSummary(BaseModel):
 #   Summaries: List[Summary]  # a list of Summary objects

@app.post("/store/")
async def store_summary(data: Union[Summary, BatchSummary]):
    try:
        # checks if its only a single summary and stores it
        if isinstance(data, Summary):   
            collection.insert_one(data.dict())
            return {"message": " A summary stored successfully"}
        elif isinstance(data, BatchSummary):
            collection.insert_many([summary.dict() for summary in data.Summaries ])
            #count = len(data.Summaries)
            return {f" {len(data.Summaries)} summaries stored"}
        else: 
            raise HTTPException(status_code=400, detail="Invalid input format.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Did not store summary: {e}")

@app.get("/summary/")
async def get_summary(original_text: str):
    try:
        returned_summary = collection.find_one({"original_text": original_text}, {"_id: 0"})
        if not returned_summary:
            raise HTTPException(status_code=404, detail="summary wasnt found.")
        return returned_summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"couldnt retrieve summary: {e}")
    
@app.get("/all_summaries/")
async def get_all_summaries():
    try:
        all_summaries = list(collection.find({}, {"_id":0}))
        logger.info(" all summaries retrieved")
        return {"summaries": all_summaries}
    except Exception as e :
        logger.error(f"couldnt retrieve the summaries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve summaries.")