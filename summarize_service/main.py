import re
import logging
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Caching the model and tokenizer for performance
MODEL_NAME = "csebuetnlp/mT5_m2m_crossSum"
logging.info("Loading model and tokenizer...")
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=False)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    logging.info("Model and tokenizer loaded successfully.")
except Exception as e:
    logging.error(f"Error loading model/tokenizer: {e}")
    raise RuntimeError(f"Failed to load model/tokenizer: {e}")

# Utility to clean whitespace
WHITESPACE_HANDLER = lambda k: re.sub(r'\s+', ' ', re.sub(r'\n+', ' ', k.strip()))

# Get the language ID for the target language
def get_lang_id(lang: str):
    try:
        return tokenizer._convert_token_to_id(
            model.config.task_specific_params["langid_map"][lang][1]
        )
    except KeyError:
        logging.error(f"Invalid target language: {lang}")
        raise HTTPException(status_code=400, detail=f"Unsupported target language: {lang}")

# FastAPI app initialization
app = FastAPI()

# Input schema
class SummarizationRequest(BaseModel):
    text: str
    tier: Optional[str] = "freemium"  # Default to "freemium"
    max_length: Optional[int] = 84
    target_lang: Optional[str] = "english"  # Default to English

@app.post("/summarize")
async def summarize(request: SummarizationRequest):
    try:
        logging.info(f"Received summarization request: {request.dict()}")

        # Validate tier
        if request.tier == "freemium" and request.target_lang != "english":
            logging.warning(
                "Freemium tier does not support cross-lingual summarization."
            )
            raise HTTPException(
                status_code=400,
                detail="Freemium tier does not support target_lang. Upgrade to premium for cross-lingual summarization."
            )

        # clean the input text so it can handle paragraphs
        input_text = WHITESPACE_HANDLER(request.text)

        # Prepare input IDs
        input_ids = tokenizer(
            [input_text],
            return_tensors="pt",
            padding="max_length",
            truncation=True,
            max_length=512,
        )["input_ids"]

        # Generate output
        decoder_start_token_id = get_lang_id(request.target_lang)
        output_ids = model.generate(
            input_ids=input_ids,
            decoder_start_token_id=decoder_start_token_id,
            max_length=request.max_length,
            no_repeat_ngram_size=2,
            num_beams=4,
        )[0]

        # Decode the output
        summary = tokenizer.decode(
            output_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )

        logging.info("Summarization completed successfully.")
        # Return response
        return {
            "summary": summary,
            "tier": request.tier,
            "target_lang": request.target_lang,
        }

    except HTTPException as http_exc:
        logging.warning(f"HTTP exception occurred: {http_exc.detail}")
        raise http_exc
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred.")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Global exception caught: {exc}")
    return HTTPException(status_code=500, detail="An unexpected error occurred.")
