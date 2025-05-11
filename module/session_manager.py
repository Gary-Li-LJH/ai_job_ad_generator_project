# job_ad_generator_project/module/session_manager.py
import streamlit as st
from content.predefined_data import (
    DEFAULT_JOB_AD_TEMPLATE,
    DEFAULT_JOB_DESCRIPTION,
    PREDEFINED_TEMPLATES, # Import the dicts to check keys
    PREDEFINED_DESCRIPTIONS
)

# Determine safe default preset keys
default_template_key = "Default Modern Template"
if default_template_key not in PREDEFINED_TEMPLATES:
    default_template_key = list(PREDEFINED_TEMPLATES.keys())[0] if PREDEFINED_TEMPLATES else "Custom"
    # If even PREDEFINED_TEMPLATES is empty (e.g. no built-ins and no files), default to "Custom" and empty template

default_description_key = "Senior Software Engineer (Backend)"
if default_description_key not in PREDEFINED_DESCRIPTIONS:
    default_description_key = list(PREDEFINED_DESCRIPTIONS.keys())[0] if PREDEFINED_DESCRIPTIONS else "Custom"


def initialize_session_state():
    """Initializes all session state variables if they don't exist."""
    defaults = {
        "job_ad_template": PREDEFINED_TEMPLATES.get(default_template_key, DEFAULT_JOB_AD_TEMPLATE), # Fallback
        "job_description": PREDEFINED_DESCRIPTIONS.get(default_description_key, DEFAULT_JOB_DESCRIPTION), # Fallback
        "generated_job_ad": "",
        "initial_generation_done": False,
        "show_chat_interface": False,
        "chat_session": None,
        "model_instance": None,
        "vertex_ai_initialized": False,
        "tone_config": "Professional & Engaging",
        "max_words_config": 0,
        "selected_template_preset": default_template_key,
        "selected_description_preset": default_description_key,
    }

    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value