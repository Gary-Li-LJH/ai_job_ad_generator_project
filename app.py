# job_ad_generator_project/app.py
import streamlit as st
import sys
import os
import yaml
import streamlit_authenticator as stauth

# --- Page Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from configs import app_settings
from module import session_manager, vertex_service, ui_components

st.set_page_config(layout=app_settings.PAGE_LAYOUT, page_title=app_settings.PAGE_TITLE, initial_sidebar_state="expanded")

# --- Load Credentials ---
try:
    with open(app_settings.CREDENTIALS_FILE_PATH, 'r') as file:
        config_auth = yaml.load(file, Loader=yaml.SafeLoader)
except FileNotFoundError:
    st.error(f"FATAL: Credentials file not found at {app_settings.CREDENTIALS_FILE_PATH}. App cannot start.")
    st.stop()
except Exception as e:
    st.error(f"FATAL: Error loading credentials file: {e}. App cannot start.")
    st.stop()

# --- Initialize Authenticator (once per session) ---
if 'authenticator' not in st.session_state:
    st.session_state.authenticator = stauth.Authenticate(
        config_auth['credentials'],
        config_auth['cookie']['name'],
        config_auth['cookie']['key'],
        config_auth['cookie']['expiry_days']
    )
authenticator = st.session_state.authenticator

# --- Sidebar handles login/logout display ---
ui_components.render_sidebar(authenticator) # This will render login in sidebar if not authenticated

# --- Main Application Logic based on Authentication Status ---
if st.session_state.get("authentication_status") is True:
    # --- USER IS AUTHENTICATED ---
    name = st.session_state.get("name")

    if not st.session_state.get("app_session_initialized"):
        session_manager.initialize_session_state()
        st.session_state.app_session_initialized = True

    if not st.session_state.get('vertex_ai_initialized', False) and \
       not st.session_state.get('model_instance', None):
        model, initialized = vertex_service.init_vertex_ai()
        if initialized:
            st.session_state.model_instance = model
            st.session_state.vertex_ai_initialized = True

    # --- Main Application UI for Authenticated Users ---
    st.title("📝 AI-Powered Job Ad Generator")
    st.markdown(f"Welcome *{name}*! Create compelling job advertisements...")

    if not st.session_state.get('vertex_ai_initialized', False):
        st.warning("Vertex AI is not initialized. Core AI features may be unavailable.")
    else:
        main_col1, main_col2 = st.columns(2)
        with main_col1:
            st.subheader("1. Input Your Details")
            with st.expander("Job Ad Template (Edit as needed)", expanded=True):
                def update_template_preset_to_custom():
                    st.session_state.selected_template_preset = "Custom"
                st.session_state.job_ad_template = st.text_area(
                    "Paste or write your job ad template here:",
                    value=st.session_state.job_ad_template,
                    height=300, key="job_ad_template_input_main",
                    on_change=update_template_preset_to_custom
                )
            with st.expander("Job Description / Key Information", expanded=True):
                def update_description_preset_to_custom():
                    st.session_state.selected_description_preset = "Custom"
                st.session_state.job_description = st.text_area(
                    "Provide the specific job details, responsibilities, qualifications, etc.:",
                    value=st.session_state.job_description,
                    height=200, key="job_description_input_main",
                    on_change=update_description_preset_to_custom
                )
            if st.button("🚀 Generate Job Ad", type="primary", use_container_width=True, key="generate_ad_btn"):
                if not st.session_state.job_ad_template or not st.session_state.job_description:
                    st.warning("Please provide both a job ad template and a job description.")
                elif not st.session_state.get('model_instance', None):
                    st.error("Vertex AI model not available. Cannot generate ad.")
                else:
                    with st.spinner("AI is crafting your job ad... Please wait."):
                        generated_text = vertex_service.generate_initial_ad(
                            st.session_state.model_instance,
                            st.session_state.job_ad_template,
                            st.session_state.job_description,
                            st.session_state.tone_config,
                            st.session_state.max_words_config
                        )
                        if generated_text:
                            st.session_state.generated_job_ad = generated_text
                            st.session_state.initial_generation_done = True
                            st.session_state.show_chat_interface = False
                            st.session_state.chat_session = None
                            st.success("Job ad generated successfully!")
                            st.rerun()
                        else:
                            st.session_state.initial_generation_done = False
        
        with main_col2:
            ui_components.render_generated_ad_output() # This will render the "Review and Refine" section
            if st.session_state.get('show_chat_interface', False):
                ui_components.render_chat_interface() # This renders chat below the ad output

    st.markdown("---")
    st.caption("Powered by Google Vertex AI Gemini & Streamlit")
    if not st.session_state.get('vertex_ai_initialized', False):
        st.caption("⚠️ Vertex AI features currently disabled.")

elif st.session_state.get("authentication_status") is False:
    # Main area content when login failed (login form is in sidebar)
    st.error('Username/password is incorrect. Please try again in the sidebar.')
    _, welcome_col, _ = st.columns([1, 2, 1]) # Centering column
    with welcome_col:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-weight: bold;'>Welcome</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #4A4A4A;'>to the {app_settings.PAGE_TITLE}</h3>", unsafe_allow_html=True)

elif st.session_state.get("authentication_status") is None:
    # Main area content when not logged in yet (login form is in sidebar)
    _, welcome_col, _ = st.columns([1, 2, 1]) # Centering column
    with welcome_col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; font-weight: bold;'>Welcome</h1>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #4A4A4A;'>to the {app_settings.PAGE_TITLE}</h3>", unsafe_allow_html=True)
        st.info("Please log in using the form in the sidebar to begin.")