import json
import logging
import os
import re
import zipfile
from typing import List, Dict, Set, Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from spacy import Language

from config import (
    DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP, CHECKPOINT_PATH
    )

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import streamlit as st

import tempfile


def handle_uploaded_file(uploaded_file):
    """
    Read the uploaded file and write its content to a temporary file.
    Returns the path to the temporary file.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".txt") as tmpfile:
            file_content = uploaded_file.getvalue().decode("utf-8")
            tmpfile.write(file_content)
            return tmpfile.name
    except Exception as e:
        st.error(f"Error handling uploaded file: {e}")
        return None


def split_text(file_path: str, chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> \
        List[str]:
    """Attempt to open and read the file, splitting its content into chunks."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except FileNotFoundError:
        logging.error(f"The file {file_path} was not found.")
        return []
    except IOError as e:
        logging.error(f"Unable to read the file {file_path}. Error: {e}")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, is_separator_regex=False
            )
    return text_splitter.split_text(text)


def clear_checkpoint(checkpoint_path: str = CHECKPOINT_PATH) -> None:
    """Remove the checkpoint file to reset the extraction process."""
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
        logging.info(f"Checkpoint at {checkpoint_path} has been reset.")


def write_checkpoint(checkpoint_path: str, processed_chunks: int, entities: Dict[str, Set[str]]) -> None:
    """Saves current processing state to a checkpoint file."""
    entity_data = {key: list(value) for key, value in entities.items()}
    try:
        with open(checkpoint_path, 'w') as f:
            json.dump(
                    {
                            'processed_chunks': processed_chunks, **entity_data
                            }, f
                    )
    except (IOError, ValueError, TypeError) as e:
        logging.error(f"Unable to save checkpoint to {checkpoint_path}. Error: {e}")


def checkpoint_operations(processed_chunks: int, entities: Dict[str, Set[str]], checkpoint_path: str, operation: str):
    """Handle checkpoint read/write/reset operations."""
    if operation == "reset":
        if os.path.exists(checkpoint_path):
            os.remove(checkpoint_path)
            logging.info("Checkpoint reset.")
    elif operation == "write":
        data = {key: list(value) for key, value in entities.items()}
        data['processed_chunks'] = processed_chunks
        with open(checkpoint_path, 'w') as f:
            json.dump(data, f)
    elif operation == "read":
        if os.path.exists(checkpoint_path):
            with open(checkpoint_path) as f:
                return json.load(f)
        return {
                "processed_chunks": 0,
                "people": [],
                "companies": []
                }


def process_text(
        file_path: str, nlp: Language, checkpoint_path: str = CHECKPOINT_PATH,
        custom_removals: Optional[Dict[str, List[Dict[str, str]]]] = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE, chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        reset: bool = False, processing_percentage: int = 100,
        progress_bar=None
        ) -> Dict[str, List[str]]:
    """Extract entities from text with optional checkpointing and custom removals."""
    if reset:
        checkpoint_operations(processed_chunks=0, entities={}, checkpoint_path=checkpoint_path, operation="reset")

    texts = split_text(file_path, chunk_size, chunk_overlap)
    if not texts:
        return {}

    chunks_to_process = len(texts) * processing_percentage // 100
    processed_chunks, entities = 0, {
            "people": set(),
            "companies": set()
            }
    checkpoint = checkpoint_operations(processed_chunks, entities, checkpoint_path, "read")

    processed_chunks = checkpoint.get('processed_chunks', 0)
    for key in entities:
        entities[key].update(set(checkpoint.get(key, [])))

    def process_chunk(chunk_text: str):
        """Process a single chunk of text to extract and classify entities."""
        doc = nlp(chunk_text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["people"].add(ent.text)
            elif ent.label_ == "ORG":
                entities["companies"].add(ent.text)

    try:
        total_chunks = len(texts[processed_chunks:processed_chunks + chunks_to_process])
        for i, chunk_text in enumerate(texts[processed_chunks:processed_chunks + chunks_to_process], start=1):
            process_chunk(chunk_text)

            if i % 10 == 0 or i == total_chunks:
                checkpoint_operations(processed_chunks + i, entities, checkpoint_path, "write")

            if progress_bar is not None:
                progress_bar.progress((processed_chunks + i) / total_chunks)

    except Exception as e:
        logging.error(f"An issue occurred during text processing: {e}")

    if progress_bar is not None:
        progress_bar.progress(100)

    return {key: sorted(value) for key, value in entities.items()}


def generate_annotated_preview(text, modifications):
    pattern = re.compile(r'\b\w+\b(?:[,.]?|\b)|\s+')
    annotated_preview = []
    word_to_identifier = {}
    identifier = 1

    for word in set(modifications.keys()):
        if modifications[word]:
            word_to_identifier[word] = modifications[word]
        else:
            if word not in word_to_identifier:
                word_to_identifier[word] = f"[XXX{identifier}XXX]"
                identifier += 1

    for match in pattern.finditer(text):
        token = match.group()
        word = token.strip(".,;:!? ")
        if word in word_to_identifier:
            replacement = word_to_identifier[word]
            annotated_preview.append((word, replacement)) if replacement != token else annotated_preview.append(token)
        else:
            annotated_preview.append(token)

    return annotated_preview


def anonymize_text(file_path: str, modifications: Dict[str, str], start_identifier=1) -> str:
    """Anonymize or alter names in text, applying unique identifiers or replacements."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        return ""

    word_to_identifier = {}
    identifier = start_identifier
    for word in set(modifications.keys()):
        if modifications[word]:  # Custom replacement provided
            replacement = modifications[word]
        else:  # Assign a unique identifier
            replacement = f"[XXX{identifier}XXX]"
            identifier += 1
        word_to_identifier[word] = replacement
        pattern = rf"\b{word}\b"
        text = re.sub(pattern, replacement, text)

    output_zip_path = "anonymized_text_and_mappings.zip"
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        zipf.writestr('modified_text.txt', text)
        mappings_csv = "Replacement,Original\n" + "\n".join(f"{v},{k}" for k, v in word_to_identifier.items())
        zipf.writestr('mappings.csv', mappings_csv)

    return output_zip_path
