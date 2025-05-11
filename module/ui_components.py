# job_ad_generator_project/module/ui_components.py
import streamlit as st
from configs.app_settings import ABSOLUTE_LOGO_PATH
from content.predefined_data import PREDEFINED_TEMPLATES, PREDEFINED_DESCRIPTIONS
from . import vertex_service # Relative import for sibling module

def render_sidebar(authenticator): # Authenticator is passed in
    """Renders the sidebar contents, including login/logout and app configurations."""
    with st.sidebar:
        try:
            st.image(ABSOLUTE_LOGO_PATH, width=150)
        except Exception: 
            st.caption("Logo not found (optional)")

        # Authentication display: Login form or Welcome/Logout button
        if st.session_state.get("authentication_status"):
            st.write(f'Welcome *{st.session_state.get("name", "User")}*')
            # Use a unique key for the logout button to avoid conflicts
            authenticator.logout('Logout', 'sidebar', key='auth_logout_button') 
        else:
            # This call renders the login form if not authenticated and handles submission.
            # It internally updates st.session_state.authentication_status, name, username.
            authenticator.login(location='sidebar') 
        
        st.markdown("---") # Visual separator
        
        # Configuration options are shown only if the user is authenticated
        if st.session_state.get("authentication_status"):
            st.title("⚙️ Configuration")
            st.subheader("Generation Settings")
            tone_options = ["Professional & Engaging", "Formal", "Friendly & Casual", "Technical & Direct", "Creative & Unique"]
            current_tone = st.session_state.get('tone_config', "Professional & Engaging")
            current_tone_index = tone_options.index(current_tone) if current_tone in tone_options else 0
            st.session_state.tone_config = st.selectbox(
                "Desired Tone:", options=tone_options, index=current_tone_index, key="tone_sb_config"
            )
            st.session_state.max_words_config = st.number_input(
                "Approximate Max Words:", min_value=0, value=st.session_state.get('max_words_config', 0),
                step=50, key="max_words_config_input"
            )
            st.markdown("---")
            st.subheader("Load Presets")

            # Template Presets
            template_preset_options = ["Custom"] + list(PREDEFINED_TEMPLATES.keys())
            # Store current value before widget to compare for changes, avoiding immediate rerun loop
            key_tp_before = 'selected_template_preset_before_widget'
            st.session_state[key_tp_before] = st.session_state.get('selected_template_preset', "Custom")
            current_tp_index = template_preset_options.index(st.session_state[key_tp_before]) \
                if st.session_state[key_tp_before] in template_preset_options else 0
            
            selected_template_key = st.selectbox(
                "Load Job Ad Template:", options=template_preset_options, index=current_tp_index,
                key="template_loader_sb"
            )
            if selected_template_key != st.session_state[key_tp_before]:
                st.session_state.selected_template_preset = selected_template_key
                if selected_template_key != "Custom":
                    st.session_state.job_ad_template = PREDEFINED_TEMPLATES[selected_template_key]
                # No need to pop key_tp_before, it will be overwritten next run correctly
                st.rerun()

            # Description Presets
            description_preset_options = ["Custom"] + list(PREDEFINED_DESCRIPTIONS.keys())
            key_dp_before = 'selected_description_preset_before_widget'
            st.session_state[key_dp_before] = st.session_state.get('selected_description_preset', "Custom")
            current_dp_index = description_preset_options.index(st.session_state[key_dp_before]) \
                if st.session_state[key_dp_before] in description_preset_options else 0

            selected_description_key = st.selectbox(
                "Load Job Description:", options=description_preset_options, index=current_dp_index,
                key="description_loader_sb"
            )
            if selected_description_key != st.session_state[key_dp_before]:
                st.session_state.selected_description_preset = selected_description_key
                if selected_description_key != "Custom":
                    st.session_state.job_description = PREDEFINED_DESCRIPTIONS[selected_description_key]
                st.rerun()
        elif st.session_state.get("authentication_status") is False and 'authenticator' in st.session_state:
             # If login failed (handled by app.py's main area), sidebar shows minimal info or can be empty here.
             # st.sidebar.error("Login failed. Check credentials.") # Or handled in main.
             pass 

def _clean_ai_response_for_ad_update(raw_response_text: str) -> str:
    """Attempts to strip common conversational preambles from the AI's response."""
    cleaned_text = raw_response_text.strip()
    # Order preambles from more specific/longer to shorter to avoid premature shorter matches
    preambles = [
        "Okay, here's the revised job ad incorporating your changes:",
        "Alright, I've updated the job ad as requested. Here it is:",
        "Okay, here's a revised job ad incorporating", # Note: this is a substring of one above
        "Okay, here's the revised job ad:",
        "Sure, here is the updated version:",
        "Here's the updated job advertisement:",
        "Okay, I've updated the ad:",
        "Here's the revised ad:",
        "Here it is:",
    ]
    for preamble in preambles:
        if cleaned_text.lower().startswith(preamble.lower()):
            # Strip preamble and leading whitespace from the rest
            potential_ad_content = cleaned_text[len(preamble):].lstrip()
            # Heuristic: check if the remaining text plausibly starts a job ad
            if potential_ad_content and (
                potential_ad_content.lower().startswith("**job title:**") or \
                potential_ad_content.lower().startswith("job title:") or \
                potential_ad_content.lower().startswith("**position title:**") or \
                potential_ad_content.lower().startswith("position title:")
            ):
                return potential_ad_content # Return the stripped content
    return raw_response_text.strip() # Return original (but stripped) if no preamble matched


def render_generated_ad_output():
    """Renders the 'Review and Refine' section, with a frame around the ad content."""
    
    st.subheader("2. Review and Refine") # Main title for this section - OUTSIDE any frame

    if st.session_state.get('initial_generation_done', False):
        # --- Frame for Ad Content ---
        # Use border=True if Streamlit version >= 1.20. Set to False for no visible border.
        container_border_for_ad = True 
        
        with st.container(border=container_border_for_ad):
            st.markdown("#### Generated Job Ad:") # Title for the ad content INSIDE the frame
            
            height_generated_ad_area = 400
            if st.session_state.get('show_chat_interface', False):
                # Reduce height if chat will also be shown, to try and fit more on screen
                height_generated_ad_area = 250 
                
            st.text_area(
                "Job Ad Content", # Label for the text_area itself
                value=st.session_state.generated_job_ad, 
                height=height_generated_ad_area,
                key="generated_ad_display_in_frame", # Unique key
                help="You can select and copy text from here.",
                label_visibility="collapsed" # Hide label if markdown title is preferred
            )
        # --- End of Frame for Ad Content ---

        # Buttons are OUTSIDE and BELOW the ad content frame
        # st.markdown("---") # Visual separator
        
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            st.download_button(
                label="📥 Download (.txt)", data=st.session_state.generated_job_ad,
                file_name="job_advertisement.txt", mime="text/plain",
                use_container_width=True, key="download_btn_main_ui" # Ensure unique key
            )
        with button_col2:
            if st.button("📋 Copy Text", use_container_width=True, key="copy_btn_main_ui"):
                st.toast("Text ready to be copied from the text area above!")
        with button_col3:
            if st.button("💬 Fine-tune with AI Chat", use_container_width=True, key="finetune_btn_main_ui"):
                st.session_state.show_chat_interface = not st.session_state.show_chat_interface
                # Initialize chat session if it's being shown for the first time OR if it's empty
                if st.session_state.show_chat_interface and \
                   (st.session_state.get('chat_session') is None or \
                    not hasattr(st.session_state.chat_session, 'history') or \
                    (hasattr(st.session_state.chat_session, 'history') and not st.session_state.chat_session.history)): # Check for empty history too
                    if st.session_state.get('model_instance') and st.session_state.get('generated_job_ad'):
                        st.session_state.chat_session = vertex_service.initialize_chat_session_with_context(
                            st.session_state.model_instance, st.session_state.generated_job_ad
                        )
                    else:
                        st.warning("Cannot initialize chat: Model or generated ad not ready.")
                st.rerun()
        
        # No horizontal line immediately after buttons, chat interface will follow if active.

    elif not st.session_state.get('initial_generation_done', False) and st.session_state.get('vertex_ai_initialized', False):
         st.info("👆 Provide template and description, then click 'Generate Job Ad'.")


def render_chat_interface():
    """Renders the chat interface for fine-tuning. This appears below the ad output and buttons."""
    chat_container_height = 300 # Fixed height for the scrollable chat log

    if st.session_state.get('show_chat_interface', False) and st.session_state.get('vertex_ai_initialized', False):
        st.markdown("---") # Separator before the chat section starts
        st.subheader("Fine-tune the Ad via Chat")
        st.caption("The AI uses the ad displayed above as context.")
        
        # Container for the chat log itself
        container_border_for_chat = True # Set to False for no border if preferred or for older Streamlit
        with st.container(height=chat_container_height, border=container_border_for_chat): 
            # Ensure chat session is initialized if it's supposed to be shown but is missing
            if st.session_state.get('chat_session') is None:
                if st.session_state.get('model_instance') and st.session_state.get('generated_job_ad'):
                    st.session_state.chat_session = vertex_service.initialize_chat_session_with_context(
                        st.session_state.model_instance, st.session_state.generated_job_ad
                    )
                if st.session_state.get('chat_session') is None: # Still None after attempt
                    st.warning("Chat session could not be initialized. Try generating an ad again.")
                    return 

            # Display chat history
            if st.session_state.chat_session and hasattr(st.session_state.chat_session, 'history') and st.session_state.chat_session.history:
                for message in st.session_state.chat_session.history:
                    role_map = {"user": "user", "model": "assistant"}
                    message_role_str = role_map.get(message.role, "assistant") # Default to assistant
                    with st.chat_message(message_role_str):
                        msg_text = ""
                        if message.parts: # Check if parts exist and is not empty
                            try: 
                                msg_text = message.parts[0].text
                            except AttributeError: # If parts[0] doesn't have .text (e.g. not a Part object)
                                msg_text = str(message.parts[0]) 
                            except IndexError: # If message.parts is an empty list
                                msg_text = "*AI processing or empty message part.*"
                        if msg_text: 
                            st.markdown(msg_text)
                        else: # If msg_text ended up empty (e.g. parts existed but text was empty)
                            st.markdown("*AI processing or empty message part.*")
            else:
                st.info("Chat history is empty. Start by asking the AI to refine the ad.")
        
        # Chat input is BELOW the bordered chat log container
        if user_chat_prompt := st.chat_input("How can I refine the ad for you? (e.g., 'Make it more formal')", key="chat_refine_input_main_ui"): # Unique key
            if st.session_state.chat_session:
                # The user's prompt will be added to history by the SDK when send_message is called.
                # The chat_message context here is for the AI's *response*.
                with st.chat_message("assistant"): 
                    message_placeholder = st.empty() # For streaming AI response
                    raw_ai_response, success = vertex_service.send_chat_message(
                        st.session_state.chat_session,
                        user_chat_prompt,
                        message_placeholder
                    )
                    if success and raw_ai_response is not None:
                        cleaned_ad_for_update = _clean_ai_response_for_ad_update(raw_ai_response)
                        st.session_state.generated_job_ad = cleaned_ad_for_update
                        st.rerun() # This re-renders the entire UI, including the chat history
            else:
                st.error("Chat session not available. Please try clicking 'Fine-tune with AI Chat' again.")