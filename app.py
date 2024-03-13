import re
import subprocess
import sys
from typing import Dict

import pandas as pd
import spacy
import streamlit as st
from annotated_text import annotated_text

from spacy_extractor import process_text, generate_annotated_preview, anonymize_text, handle_uploaded_file

st.set_page_config(layout='centered', page_title="Text Anonymizer", page_icon='🔓')


@st.cache_resource
def load_model():
    """Load the NLP model, downloading it if necessary."""
    model_name = "en_core_web_trf"
    try:
        return spacy.load(model_name)
    except OSError:
        print(f"{model_name} not found, downloading...")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
        return spacy.load(model_name)


# Initialize tabs
tab1, tab2, tab3 = st.tabs(["😎 Anonymizing", "🔁 Reverse Anonymization", "ℹ️ Info"])

with tab1:
    nlp = load_model()
    st.title("🔓 Text Anonymizer")
    temp_file_path = None
    uploaded_file = st.file_uploader("Upload Text File:", type=['txt'])

    if uploaded_file is not None:
        temp_file_path = handle_uploaded_file(uploaded_file)
        if temp_file_path is None:
            st.error("Failed to process the uploaded file.")

    chunk_size = st.sidebar.slider(
        "Processing Chunk Size (Characters):", min_value=100, max_value=5000, value=1000, step=100
        )
    processing_percentage = st.sidebar.slider("Text Processing Coverage (%):", 0, 100, 100)
    # Add this line in the tab1 code block, where you define other sliders in the sidebar
    overlap_size = st.sidebar.slider(
            "Chunk Overlap Size (Characters):", min_value=0, max_value=200, value=0, step=10
            )

    reset_checkpoint = st.sidebar.checkbox("Reset Processing Checkpoint:")
    keywords = st.sidebar.text_area("Keywords for Anonymization (comma-separated):")

    custom_replacements = {keyword.strip(): "" for keyword in keywords.split(',') if keyword.strip()}

    entity_types = st.sidebar.multiselect(
            "Target Entity Types for Anonymization:", ["people", "companies"], default=["people", "companies"]
            )

    progress_bar = st.progress(0)

    process_button = st.button("🔄 Start Anonymization")

    # Adjusted: Added a placeholder for the download button to display next to the Start Anonymization button
    # download_button_placeholder = st.empty()

    if process_button and temp_file_path:
        try:
            entities = process_text(
                    file_path=temp_file_path,
                    nlp=nlp,
                    custom_removals=custom_replacements,
                    reset=reset_checkpoint,
                    chunk_overlap=overlap_size,
                    processing_percentage=processing_percentage,
                    progress_bar=progress_bar
                    )
            st.session_state['entities'] = entities
            st.session_state.show_preview = True

            zip_file_path = anonymize_text(
                    temp_file_path, st.session_state['modifications']
                    )

            with open(zip_file_path, "rb") as f:
                # Adjusted: Display the download button next to the Start Anonymization button using the placeholder
                st.download_button(
                        label="👇 Download Text & Keys",
                        data=f,
                        file_name="anonymized_text_and_mappings.zip",
                        mime="application/zip"
                        )
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

    if 'modifications' not in st.session_state:
        st.session_state['modifications'] = {}

    if 'entities' in st.session_state:
        st.success("✅ Anonymization is done, Scroll Down for preview.")
        st.subheader("Modify Replacements")
        for entity_type, words in st.session_state['entities'].items():
            with st.expander(f"{entity_type.capitalize()}"):
                for word in words:
                    input_key = f"{entity_type}_{word}"
                    with st.container():
                        initial_value = st.session_state['modifications'].get(word, "")
                        user_input = st.text_input(
                                f"Replacement for '{word}':", value="", key=input_key
                                )
                        st.session_state['modifications'][word] = user_input

    if custom_replacements:
        with st.expander("Custom Replacements"):
            for original_word in custom_replacements.keys():
                input_key = f"custom_replacement_{original_word}"
                replacement_value = st.session_state['modifications'].get(original_word, "")
                user_defined_replacement = st.text_input(f"Replacement for '{original_word}':", value="", key=input_key)
                st.session_state['modifications'][original_word] = user_defined_replacement

    if uploaded_file is not None:
        st.session_state['uploaded_file_content'] = uploaded_file.getvalue().decode("utf-8")
        st.session_state['chunk_size'] = chunk_size
        st.session_state['processing_percentage'] = processing_percentage
        st.session_state['keywords'] = keywords
        st.session_state['custom_replacements'] = custom_replacements
        st.session_state['entity_types'] = entity_types

    preview_percentage = st.slider(
            'Preview Text Coverage (%):', 0, 100, 5, key='preview_percentage'
            )

    if 'show_preview' in st.session_state and st.session_state.show_preview:
        if 'modifications' in st.session_state and 'uploaded_file_content' in st.session_state:
            preview_length = int(len(st.session_state['uploaded_file_content']) * (preview_percentage / 100.0))
            text_to_preview = st.session_state['uploaded_file_content'][:preview_length]

            with st.expander("Modified Text Preview", expanded=True):
                annotated_preview = generate_annotated_preview(text_to_preview, st.session_state['modifications'])
                annotated_text(*annotated_preview)


def reverse_anonymize_text(text: str, keys: Dict[str, str]) -> str:
    """Reverse the anonymization process using the provided keys, including unique identifiers."""
    for replacement, original in keys.items():
        if "[" in replacement and "]" in replacement:  # Check if the replacement is a unique identifier
            text = text.replace(replacement, original)
        else:
            text = re.sub(rf"\b{re.escape(replacement)}\b", original, text)
    return text


with tab2:
    st.title("🔁 Reverse Anonymization")
    uploaded_text_file = st.file_uploader("Upload Anonymized Text File:", type=['txt'], key="text_file")
    uploaded_keys_file = st.file_uploader("Upload Keys File:", type=['csv'], key="keys_file")

    if uploaded_text_file and uploaded_keys_file:
        # Process the uploaded files
        text_content = uploaded_text_file.getvalue().decode("utf-8")
        keys_content = pd.read_csv(uploaded_keys_file)
        keys_dict = pd.Series(keys_content.Original.values, index=keys_content.Replacement).to_dict()

        reversed_text = reverse_anonymize_text(text_content, keys_dict)

        # Display the reversed text or provide it for download
        st.download_button(
                label="👇️ Download Reversed Text",
                data=reversed_text,
                file_name="reversed_text.txt",
                mime="text/plain"
                )

        with st.expander("Preview Reversed Text", expanded=True):
            st.text_area("Preview", reversed_text, height=250)

with tab3:
    st.markdown(
        """
        ### How to Use the Text Anonymizer App
        
        Version: 0.1
        Last Update: Mar, 12, 2024
        
        This Streamlit app anonymizes sensitive information in text documents, focusing on specified entity types like people and companies. Here's a quick guide on how to use it:
        
        1. **Upload a Text File**: Start by uploading the text file you want to anonymize using the file uploader on the "🔧 Main" tab.
        2. **Adjust Settings (Optional)**: Use the sidebar to customize the anonymization process:
           - **Chunk Size**: Adjust the chunk size for processing the text. The default is 1000 characters.
           - **Percentage of Text to Process**: Choose what percentage of the text to anonymize.
           - **Keywords for Replacement**: Enter any specific keywords you want replaced.
           - **Entity Types**: Select which entity types (e.g., people, companies) you want to focus on.
        3. **Process Text**: Click the "🔄 Process Text" button to start the anonymization. A progress bar will show the process.
        4. **Modify Replacements (Optional)**: After processing, you can manually adjust the replacement values for each identified entity or keyword.
        5. **Preview**: Click the "🔍 Preview" button to see a portion of the anonymized text. Use the slider above the preview button to adjust the percentage of the text shown in the preview.
        6. **Download File**: Once you're satisfied with the preview, click the "⬇️ Download File" button to save the anonymized text.
        
            """
        )
