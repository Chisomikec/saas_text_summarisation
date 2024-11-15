from pydantic import BaseModel
from typing import List, Optional

class summary_req(BaseModel):  #this handles the incoming request
    
    text: Optional[str] = None
    texts: Optional[List[str]] = None
    max_length: Optional[int] = 1000
    min_length: Optional[int] = 30