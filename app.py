import streamlit as st
from PIL import Image
import pypdfium2 as pdfium
import tempfile
import io

from extractor import analyze_prescription
from export_utils import generate_pdf, generate_ics, generate_audio_summary

st.set_page_config(page_title="ClearMed", page_icon="💊", layout="wide")

st.title("💊 ClearMed: Doctor Handwriting & Medicine Explainer")
st.write("Scan a prescription via camera or upload an image/PDF to get a clear schedule.")

left_col, right_col = st.columns(2)

with left_col:
    st.subheader("1. Input Prescription")
    
    # Language Dropdown Selector
    selected_language = st.selectbox(
        "🌐 Choose Output Language:",
        [
            "English", 
            "Hindi (हिन्दी)", 
            "Spanish (Español)", 
            "French (Français)", 
            "German (Deutsch)", 
            "Bengali (বাংলা)", 
            "Tamil (தமிழ்)", 
            "Telugu (తెలుగు)"
        ]
    )

    # Input Method Tabs
    tab_upload, tab_camera = st.tabs(["📁 Upload File (Image/PDF)", "📷 Take Photo"])
    
    raw_image = None
    
    with tab_upload:
        uploaded_file = st.file_uploader(
            "Choose an image or PDF...", 
            type=["jpg", "jpeg", "png", "pdf"],
            key="file_uploader"
        )
        if uploaded_file is not None:
            if uploaded_file.name.lower().endswith(".pdf"):
                # Render the first page of the PDF to a PIL Image
                pdf_bytes = uploaded_file.read()
                pdf = pdfium.PdfDocument(pdf_bytes)
                page = pdf[0]
                bitmap = page.render(scale=2)
                raw_image = bitmap.to_pil()
                st.image(raw_image, caption="PDF First Page Preview", use_container_width=True)
            else:
                raw_image = Image.open(uploaded_file)
                st.image(raw_image, caption="Uploaded Prescription", use_container_width=True)

    with tab_camera:
        camera_photo = st.camera_input("Take a photo of the prescription", key="camera_input")
        if camera_photo is not None:
            raw_image = Image.open(camera_photo)
            st.image(raw_image, caption="Captured Photo", use_container_width=True)

with right_col:
    st.subheader("2. Decoded Medication Plan")
    
    if raw_image is not None:
        if st.button("Decode & Explain", type="primary"):
            with st.spinner(f"Decoding handwriting and analyzing in {selected_language}..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    raw_image.save(temp_file.name)
                    temp_path = temp_file.name
                
                try:
                    clean_lang = selected_language.split(" ")[0]
                    result = analyze_prescription(temp_path, target_language=clean_lang)
                    st.session_state["result"] = result
                    st.session_state["chosen_lang"] = selected_language
                except Exception as e:
                    st.error(f"Error processing image: {e}")

    # Display decoded results
    if "result" in st.session_state and raw_image is not None:
        result = st.session_state["result"]
        current_lang = st.session_state.get("chosen_lang", "English")
        
        st.success(f"Successfully Decoded in {current_lang}!")
        st.info(f"**Doctor's Summary:** {result.doctor_notes_summary}")
        
        if result.confidence_warning:
            st.warning(f"⚠️️ **Note on Handwriting:** {result.confidence_warning}")

        # Drug Interaction Section
        interactions = getattr(result, "drug_interactions", [])
        if interactions:
            st.error("🚨 **Potential Drug Interaction Warning**")
            for interaction in interactions:
                with st.expander(f"⚠️ {interaction.severity} Risk: {', '.join(interaction.medications_involved)}", expanded=True):
                    st.write(f"**Effect:** {interaction.effect}")
                    st.write(f"**Recommendation:** {interaction.clinical_recommendation}")
        else:
            st.success("✅ **No major drug interactions detected between the prescribed medications.**")
        
        st.markdown("### 📋 Daily Schedule")
        for med in result.medications:
            with st.container(border=True):
                st.markdown(f"#### 💊 **{med.name}** (`{med.dosage}`)")
                st.write(f"**What it does:** {med.purpose}")
                st.write(f"**Schedule:** {med.frequency} — *{med.timing}*")
                if med.critical_warning:
                    st.write(f"⚠️ **Caution:** {med.critical_warning}")
                    
        if result.follow_up_advice:
            st.write(f"💡 **Extra Advice:** {result.follow_up_advice}")

        # Audio Narration Section
        st.divider()
        st.markdown(f"### 🔊 Listen ({current_lang})")
        audio_bytes = generate_audio_summary(result, language=current_lang)
        st.audio(audio_bytes, format="audio/mp3")

        # Download Buttons Section
        st.divider()
        st.markdown("### 📥 Export Medication Plan")
        
        col_pdf, col_ics = st.columns(2)
        
        with col_pdf:
            pdf_data = generate_pdf(result)
            st.download_button(
                label="📄 Download PDF Summary",
                data=pdf_data,
                file_name="ClearMed_Prescription.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with col_ics:
            ics_data = generate_ics(result)
            st.download_button(
                label="📅 Add to Calendar (.ics)",
                data=ics_data,
                file_name="ClearMed_Schedule.ics",
                mime="text/calendar",
                use_container_width=True
            )
