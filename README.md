# ClearMed: Doctor Prescription & Medicine Explainer

An AI-powered application designed to transcribe handwritten doctor prescriptions, explain medication schedules and precautions in plain language, and highlight potential drug interactions.

## Features
- **Prescription Digitization**: Upload prescription images/PDFs or use camera capture.
- **Multilingual Explanations**: Understand dosages and schedules in clear, simple language.
- **Safety Checks**: Automatic drug-drug interaction detection with severity levels.
- **Export Formats**: Download as PDF summaries, ICS calendar reminders, and listen via audio.

## Tech Stack
- **Frontend**: Streamlit
- **AI / LLM**: Google Gemini API (`gemini-2.5-flash`)
- **Document Handling**: `pypdfium2`, `Pillow`
- **Exporting**: `reportlab`, `icalendar`, `gTTS`

## Local Setup
1. Clone the repository:
