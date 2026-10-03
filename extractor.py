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
4. SCREEN FOR DRUG-DRUG INTERACTIONS: Check if any medicines on this prescription have adverse interactions with each other. If none exist, leave the drug_interactions list empty.
5. If handwriting is illegible, do not guess; flag it in confidence_warning in {target_language}.
"""

def analyze_prescription(image_path: str, target_language: str = "English") -> PrescriptionAnalysis:
    image = Image.open(image_path)
    
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=[
                    image, 
                    f"Extract prescription details, cross-check interactions, and explain everything in {target_language}."
                ],
                config=types.GenerateContentConfig(
                    system_instruction=get_system_prompt(target_language),
                    response_mime_type="application/json",
                    response_schema=PrescriptionAnalysis,
                    temperature=0.1
                )
            )
            return PrescriptionAnalysis.model_validate_json(response.text)
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise e
