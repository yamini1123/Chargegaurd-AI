import json
import os
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Initialize the client
client = genai.Client()

# 1. Define the strict output schema
class ChargebackDecision(BaseModel):
    recommendation: str = Field(description="Must be exactly 'FIGHT' or 'ACCEPT'")
    confidence_score: int = Field(description="A score from 0 to 100")
    letter_text: str = Field(description="The formal representment document in markdown")

SYSTEM_PROMPT = """ You are a Senior Chargeback Defense Agent. Analyze the dispute evidence and decide:
1. Is this dispute FIGHTABLE (High chance of winning based on AVS/CVC/Delivery/Chat)?
2. If FIGHTABLE, generate a formal, bank-ready representment document.
3. If NOT FIGHTABLE (True fraud, failed delivery, failed CVC), recommend ACCEPT to avoid chargeback fees.

Formatting Rules for letter_text:
- Do NOT use top-level '#' single headers.
- Use '###' (H3 headers) for section titles like '### Executive Summary' or '### Key Evidence'.
- Output clean, unescaped Markdown paragraphs.
"""

def process_chargeback(dispute):
    prompt = f"{SYSTEM_PROMPT}\n\nChargeback Data:\n{json.dumps(dispute)}"
    
    # 2. Pass the schema into the configuration
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ChargebackDecision,
        }
    )
    
    # 3. The SDK automatically parses it into our Pydantic object
    decision = response.parsed
    
    # Convert it back to a dictionary so app.py can read it seamlessly
    return decision.model_dump()