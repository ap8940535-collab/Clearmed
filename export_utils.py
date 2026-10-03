import io
from gtts import gTTS
from fpdf import FPDF
from icalendar import Calendar, Event
import datetime
from schemas import PrescriptionAnalysis

# Mapping display names to gTTS language codes
LANG_CODES = {
    "English": "en",
    "Hindi (हिन्दी)": "hi",
    "Spanish (Español)": "es",
    "French (Français)": "fr",
    "German (Deutsch)": "de",
    "Bengali (বাংলা)": "bn",
    "Tamil (தமிழ்)": "ta",
    "Telugu (తెలుగు)": "te"
}

def clean_text(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "–": "-", "—": "-", "’": "'", "‘": "'",
        "“": '"', "”": '"', "…": "...", "•": "*", "\u2013": "-", "\u2014": "-"
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")

def generate_pdf(data: PrescriptionAnalysis) -> bytes:
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_margins(left=20, top=20, right=20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    usable_width = 170

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_x(20)
    pdf.cell(usable_width, 10, clean_text("ClearMed - Prescription Schedule"), align="C")
    pdf.set_y(pdf.get_y() + 15)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_x(20)
    pdf.cell(usable_width, 8, clean_text("Clinical Summary:"))
    pdf.set_y(pdf.get_y() + 8)
    
    pdf.set_font("Helvetica", size=10)
    pdf.set_x(20)
    pdf.multi_cell(usable_width, 6, clean_text(data.doctor_notes_summary))
    pdf.set_y(pdf.get_y() + 8)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_x(20)
    pdf.cell(usable_width, 8, clean_text("Medications & Instructions:"))
    pdf.set_y(pdf.get_y() + 10)

    for idx, med in enumerate(data.medications, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_x(20)
        pdf.cell(usable_width, 7, clean_text(f"{idx}. {med.name} ({med.dosage})"))
        pdf.set_y(pdf.get_y() + 7)

        pdf.set_font("Helvetica", size=10)
        pdf.set_x(20)
        pdf.multi_cell(usable_width, 6, clean_text(f"- Purpose: {med.purpose}"))
        pdf.set_x(20)
        pdf.multi_cell(usable_width, 6, clean_text(f"- Schedule: {med.frequency} | {med.timing}"))

        if med.critical_warning:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_x(20)
            pdf.multi_cell(usable_width, 6, clean_text(f"- Caution: {med.critical_warning}"))
        
        pdf.set_y(pdf.get_y() + 4)

    if data.follow_up_advice:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_x(20)
        pdf.cell(usable_width, 7, clean_text("Follow-Up Advice:"))
        pdf.set_y(pdf.get_y() + 7)
        
        pdf.set_font("Helvetica", size=10)
        pdf.set_x(20)
        pdf.multi_cell(usable_width, 6, clean_text(data.follow_up_advice))

    return bytes(pdf.output())

def generate_ics(data: PrescriptionAnalysis) -> bytes:
    cal = Calendar()
    cal.add('prodid', '-//ClearMed Medication Schedule//EN')
    cal.add('version', '2.0')
    start_time = datetime.datetime.now()
    
    for med in data.medications:
        event = Event()
        event.add('summary', f"Take {med.name} ({med.dosage})")
        description = (
            f"Instructions: {med.frequency} ({med.timing})\n"
            f"Purpose: {med.purpose}\n"
            f"Caution: {med.critical_warning if med.critical_warning else 'None'}"
        )
        event.add('description', description)
        event.add('dtstart', start_time)
        event.add('dtend', start_time + datetime.timedelta(minutes=15))
        cal.add_component(event)
        
    return cal.to_ical()

def generate_audio_summary(data: PrescriptionAnalysis, language: str = "English") -> bytes:
    lang_code = LANG_CODES.get(language, "en")
    
    speech_parts = [data.doctor_notes_summary]
    for idx, med in enumerate(data.medications, 1):
        line = f"{idx}: {med.name}, {med.dosage}. {med.purpose}. {med.frequency}, {med.timing}."
        if med.critical_warning:
            line += f" Caution: {med.critical_warning}"
        speech_parts.append(line)
        
    if data.follow_up_advice:
        speech_parts.append(data.follow_up_advice)

    full_speech = ". ".join(speech_parts)
    
    tts = gTTS(text=full_speech, lang=lang_code, slow=False)
    audio_buffer = io.BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0)
    return audio_buffer.read()