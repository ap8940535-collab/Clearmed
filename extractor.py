import os
import time
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from schemas import PrescriptionAnalysis

load_dotenv()

# Read from Streamlit Cloud Secrets first; fallback to environment variables
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

def get_system_prompt(target_language: str = "English") -> str:
    return f"""
You are ClearMed, an expert clinical transcription and pharmacovigilance helper.
Analyze this prescription carefully:
1. Extract drug names, strengths, frequency, and administration instructions. Keep official brand/generic medication names recognizable.
2. Translate medical shorthand (e.g., 'TDS' = 'Three times a day', 'OD' = 'Once daily', 'PC' = 'After meals').
3. Explain each drug's purpose, instructions, summary, cautions, and interaction warnings in {target_language}.
4. SCREEN FOR DRUG-DRUG INTERACTIONS: Check if any medicines on this prescription have adverse interactions with each other. If none exist, state that clearly.
5. If handwriting is illegible, do not guess; flag it in confidence_warning in {target_language}.
"""

def analyze_prescription(image_path: str, target_language: str = "English") -> PrescriptionAnalysis:
    image = Image.open(image_path)
    
    # Models to try in order
    candidate_models = ["gemini-3.8-flash", "gemini-1.5-flash"]
    last_error = None

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[get_system_prompt(target_language), image],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=PrescriptionAnalysis,
                ),
            )
            return PrescriptionAnalysis.model_validate_json(response.text)
        except Exception as e:
            last_error = e
            # If rate limit or quota exceeded, try the next model
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                continue
            raise e

    raise last_error
