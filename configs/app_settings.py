# job_ad_generator_project/configs/app_settings.py
import os
from vertexai.generative_models import HarmCategory, HarmBlockThreshold

# --- Path Configuration ---
# Path to the project root (where app.py is)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Go up two levels from app_settings.py

KEYS_DIR = os.path.join(PROJECT_ROOT, "keys")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
AD_TEMPLATES_DIR = os.path.join(CONTENT_DIR, "ad_templates")
JD_DESCRIPTIONS_DIR = os.path.join(CONTENT_DIR, "jd_descriptions")


# --- Service Account Configuration ---
SERVICE_ACCOUNT_FILE_NAME = "hadoopdemo-proj-fdab20141a22.json" # YOUR KEY FILE NAME
SERVICE_ACCOUNT_FILE_PATH = os.path.join(KEYS_DIR, SERVICE_ACCOUNT_FILE_NAME)

# --- Vertex AI Configuration ---
PROJECT_ID = "hadoopdemo-proj"  # Replace with your Project ID!
LOCATION = "us-central1"        # Replace with your Location!
MODEL_NAME = "gemini-2.0-flash-001" # Or your preferred model

# --- Safety Settings ---
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}

# --- Application Settings ---
PAGE_TITLE = "AI Job Ad Generator"
PAGE_LAYOUT = "wide"
LOGO_FILE_NAME = "job_ad_logo.png"
ABSOLUTE_LOGO_PATH = os.path.join(ASSETS_DIR, LOGO_FILE_NAME)

# --- Authentication Configuration ---
CREDENTIALS_FILE_PATH = os.path.join(PROJECT_ROOT, "configs", "credentials.yaml")


# --- Vertex AI Authentication Configuration ---
# Choose the authentication method for Vertex AI. Options:
# "ADC": Application Default Credentials.
#        - For local: Run `gcloud auth application-default login`.
#        - For Cloud Run: Relies on the service account assigned to the Cloud Run service.
# "KEY_FILE": Use a specific service account JSON key file.
#             The path is specified by SERVICE_ACCOUNT_FILE_PATH below.
# Default to "ADC", which is generally recommended for portability and Cloud Run.
VERTEX_AI_AUTH_METHOD = "KEY_FILE"  # Or "ADC"