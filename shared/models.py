from pydantic import BaseModel
from typing import List, Optional

#class summary_req(BaseModel):  #this handles the incoming request
    
 #   text: Optional[str] = None
  #  texts: Optional[List[str]] = None
    #max_length: Optional[int] = 1000
    #min_length: Optional[int] = 30
    

# Request model for summarization
class SummaryRequest(BaseModel):
    text: Optional[str] = None
    #texts: Optional[List[str]] = None
    tier: Optional[str] = "freemium"
    target_lang: Optional[str] = "english"
    max_length: Optional[int] = 84

# Single summary record for storage
class Summary(BaseModel):
    original_text: str
    summarized_text: str

# Batch summary for multiple records
class BatchSummary(BaseModel):
    summaries: List[Summary]
