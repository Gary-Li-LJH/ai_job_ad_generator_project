# job_ad_generator_project/module/vertex_service.py

"""
Vertex AI Service Module

This module handles all interactions with Google Vertex AI, including:
- Initialization of the Vertex AI client and generative model.
- Generation of the initial job advertisement.
- Management of chat sessions for refining job ads.
"""

import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Part, Content
from google.oauth2 import service_account # For loading credentials from a key file
import os

# Import necessary configurations from the central application settings
from configs.app_settings import (
    VERTEX_AI_AUTH_METHOD,
    SERVICE_ACCOUNT_FILE_PATH, # Used only if VERTEX_AI_AUTH_METHOD is "KEY_FILE"
    PROJECT_ID,
    LOCATION,
    MODEL_NAME,
    SAFETY_SETTINGS
)

# Module-level flag to indicate if Vertex AI has been successfully initialized in this process run.
# Note: app.py uses st.session_state['vertex_ai_initialized'] to manage this across Streamlit reruns.
_vertex_ai_successfully_initialized_this_run = False

def init_vertex_ai():
    """
    Initializes the Vertex AI SDK and the specified generative model.

    The authentication method is determined by the `VERTEX_AI_AUTH_METHOD`
    setting in `configs/app_settings.py`:
    - "ADC": Uses Application Default Credentials. Ideal for Cloud Run or local
             development after `gcloud auth application-default login`.
    - "KEY_FILE": Uses a specific service account JSON key file defined by
                  `SERVICE_ACCOUNT_FILE_PATH` in `configs/app_settings.py`.

    Returns:
        tuple: (GenerativeModel instance, bool indicating success) or (None, False) on failure.
    """
    global _vertex_ai_successfully_initialized_this_run

    # While vertexai.init() can be called multiple times, we avoid redundant setup
    # if we've already successfully done so in this Python process instance.
    # The st.session_state in app.py is the primary gatekeeper for app-level sessions.
    # if _vertex_ai_successfully_initialized_this_run:
    #     print("DEBUG: Vertex AI init_vertex_ai called, but already flagged as initialized in this run.")
    #     # This logic might need adjustment if the model object needs to be re-fetched.
    #     # For now, assuming app.py calls this once and stores the model.

    print(f"DEBUG: Attempting Vertex AI initialization. Preferred method: {VERTEX_AI_AUTH_METHOD}")
    credentials_object = None # Will hold credentials if using a key file

    try:
        if VERTEX_AI_AUTH_METHOD == "ADC":
            print("DEBUG: Initializing Vertex AI with Application Default Credentials (ADC)...")
            # For ADC, no explicit credentials object is passed to vertexai.init().
            # The library automatically discovers them if ADC is set up.
            vertexai.init(project=PROJECT_ID, location=LOCATION)
            print("DEBUG: Vertex AI SDK initialized using ADC.")

        elif VERTEX_AI_AUTH_METHOD == "KEY_FILE":
            if not SERVICE_ACCOUNT_FILE_PATH:
                error_msg = "Vertex AI Auth Error: Method is 'KEY_FILE' but SERVICE_ACCOUNT_FILE_PATH is not set in app_settings.py."
                st.error(error_msg)
                print(f"ERROR: {error_msg}")
                return None, False
            if not os.path.exists(SERVICE_ACCOUNT_FILE_PATH):
                error_msg = f"Vertex AI Auth Error: Method is 'KEY_FILE' but key file not found at specified path: '{SERVICE_ACCOUNT_FILE_PATH}'"
                st.error(error_msg)
                print(f"ERROR: {error_msg}")
                return None, False
            
            print(f"DEBUG: Initializing Vertex AI with Service Account Key File: {SERVICE_ACCOUNT_FILE_PATH}")
            credentials_object = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE_PATH)
            vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials_object)
            print("DEBUG: Vertex AI SDK initialized using configured key file.")
        
        else:
            error_msg = f"Invalid VERTEX_AI_AUTH_METHOD: '{VERTEX_AI_AUTH_METHOD}'. Must be 'ADC' or 'KEY_FILE'."
            st.error(error_msg)
            print(f"ERROR: {error_msg}")
            return None, False

        # If vertexai.init() was successful by any chosen method:
        model = GenerativeModel(MODEL_NAME, safety_settings=SAFETY_SETTINGS)
        print(f"DEBUG: Vertex AI Model '{MODEL_NAME}' loaded successfully.")
        _vertex_ai_successfully_initialized_this_run = True
        return model, True

    except FileNotFoundError: # Should be caught by os.path.exists for KEY_FILE method
        st.error(f"Vertex AI Init Error (KEY_FILE): Specified service account key file not found. Path: {SERVICE_ACCOUNT_FILE_PATH}")
        print(f"ERROR: FileNotFoundError during Vertex AI init (KEY_FILE): {SERVICE_ACCOUNT_FILE_PATH}")
        return None, False
    except Exception as e:
        st.error(f"Error initializing Vertex AI (Method: '{VERTEX_AI_AUTH_METHOD}'): {e}")
        print(f"ERROR: During Vertex AI init (Method: '{VERTEX_AI_AUTH_METHOD}'): {e}")
        # For more detailed server-side debugging:
        # import traceback
        # traceback.print_exc()
        return None, False

def generate_initial_ad(model: GenerativeModel, template: str, description: str, tone: str, max_words: int) -> str | None:
    """
    Generates the initial job advertisement using the provided model and inputs.

    Args:
        model: The initialized GenerativeModel instance.
        template: The job ad template string.
        description: The job description string or key information.
        tone: The desired tone for the advertisement.
        max_words: Approximate maximum word count (0 for no strict limit).

    Returns:
        The generated job advertisement text as a string, or None on failure.
    """
    if not model:
        st.error("Vertex AI Model not available for ad generation. Please check initialization.")
        print("ERROR: generate_initial_ad called with no model.")
        return None

    # Construct configuration instructions for the prompt
    config_instructions = f"\nAdopt a '{tone}' tone for the advertisement."
    if max_words > 0:
        config_instructions += f"\nTry to keep the advertisement approximately under {max_words} words."
    else:
        config_instructions += "\nThere is no strict word limit, but aim for clarity and conciseness appropriate for a job ad."

    # Construct the full prompt for the LLM
    prompt = f"""
You are an expert HR copywriter specializing in creating compelling job advertisements.
Your task is to generate a complete and engaging job advertisement based on the provided template, job description, and specific instructions.

**INSTRUCTIONS FOR GENERATION:**
1.  **Adherence to Template:** Strictly use the following TEMPLATE as the primary structure and guide for the sections and their order:
    <template>
    {template}
    </template>

2.  **Content Integration:** Fill in the template placeholders and expand upon its sections using the detailed information from this JOB DESCRIPTION:
    <job_description>
    {description}
    </job_description>

3.  **Tone and Word Count:**
    {config_instructions}

4.  **Elaboration and Creativity:**
    *   If the template has sections like "About Us" or "Why Join Us?", and the job description lacks explicit text for these, use your HR expertise to write plausible, positive, and attractive content. You can infer company culture aspects if not directly stated.
    *   If placeholders like "[Insert Job Title Here]" are present, ensure they are filled based on the job description.
    *   Ensure the language is inclusive and appealing to a diverse range of candidates.

5.  **Output Format:**
    *   The output should be the complete job advertisement text ONLY.
    *   Do not include any of your own commentary, introductions, or sign-offs (like "Generated Job Advertisement:" or "Here is the job ad:") before or after the actual advertisement content.
    *   Preserve formatting (like bullet points, bolding indicated by asterisks in the template) as much as possible.

Begin the job advertisement now:
"""
    try:
        print(f"DEBUG: Sending prompt to Vertex AI for initial ad generation (first 50 chars): {prompt[:50]}...")
        response = model.generate_content(prompt)
        print("DEBUG: Received response from Vertex AI for initial ad generation.")
        return response.text
    except Exception as e:
        error_msg = f"An error occurred during ad generation: {e}"
        st.error(error_msg)
        print(f"ERROR: Ad generation failed. Details: {error_msg}")
        return None

def initialize_chat_session_with_context(model: GenerativeModel, generated_ad_text: str) -> ChatSession | None:
    """
    Initializes or re-initializes a chat session, priming it with the current job ad
    and instructions for AI behavior during fine-tuning.

    Args:
        model: The initialized GenerativeModel instance.
        generated_ad_text: The current full text of the job advertisement.

    Returns:
        A new ChatSession instance, or None on failure.
    """
    if not model:
        st.error("Vertex AI Model not available for chat initialization.")
        print("ERROR: initialize_chat_session_with_context called with no model.")
        return None

    # This priming message is crucial for controlling the AI's output format during chat.
    initial_assistant_message_content = f"""
Okay, I'm ready to help you refine the job ad. Here is the current version:

--- START OF CURRENT JOB AD ---
{generated_ad_text}
--- END OF CURRENT JOB AD ---

**CRITICAL INSTRUCTIONS FOR OUR INTERACTION (Please Read Carefully):**

1.  **Your Primary Goal:** Your main task is to help me refine the job advertisement above.
2.  **Responding to Ad Refinement Requests:** When I ask you to make changes to the job ad (e.g., "change the location," "make the tone more formal"), your response **MUST BE ONLY the complete, revised job advertisement text**.
    *   Do NOT include any conversational phrases, introductions, explanations, or sign-offs before or after the job ad text itself.
    *   **Example - CORRECT Response (Only the ad):**
        ```
        **Job Title:** [Job Title]
        **Company:** [Company Name]
        **Location:** New York, NY 
        ... (rest of the complete ad) ...
        ```
    *   **Example - INCORRECT Response (Do NOT do this):**
        ```
        Okay, I've updated the location for you! Here's the new ad:
        **Job Title:** [Job Title]
        ...
        ```
3.  **Responding to General/Unrelated Questions:** If I ask you a question that is NOT about refining the current job ad (e.g., "What's your name?", "Can you tell me a joke?"), you can answer it naturally and conversationally. You are NOT restricted to outputting only the job ad in these cases.
4.  **Returning to Ad Refinement:** After any general conversation, if I then ask you to make a change to the job ad again, you **MUST immediately switch back to following Instruction #2**. That is, your response for that ad refinement request must again be ONLY the complete, revised job advertisement text, without any preamble.
5.  **Output Format for Ad:** When providing the job ad, preserve formatting (like bullet points and bolding) as indicated in the original template or current ad structure.

I will rely on you to follow these instructions strictly, especially the output format for ad refinements, so the application can process your response correctly.

What changes would you like to make to the job ad displayed above?
"""
    # This message is from the "model" (assistant's) perspective, setting the stage.
    initial_model_content = Content(
        role="model",
        parts=[Part.from_text(initial_assistant_message_content)]
    )
    
    try:
        chat_session = model.start_chat(history=[initial_model_content])
        print("DEBUG: New chat session initialized with context.")
        return chat_session
    except Exception as e:
        st.error(f"Error initializing chat session: {e}")
        print(f"ERROR: Chat session initialization failed: {e}")
        return None

def send_chat_message(chat_session: ChatSession, user_prompt: str, message_placeholder) -> tuple[str | None, bool]:
    """
    Sends a user's message to the ongoing chat session and streams the AI's response.

    Args:
        chat_session: The active ChatSession instance.
        user_prompt: The user's input string.
        message_placeholder: A Streamlit empty placeholder to stream the response into.

    Returns:
        tuple: (The AI's full response text or None on error, bool indicating success).
               Success is False if the response was blocked, empty, or an error occurred.
    """
    if not chat_session:
        st.error("Chat session is not available. Cannot send message.")
        print("ERROR: send_chat_message called with no chat_session.")
        if message_placeholder:
            message_placeholder.error("Chat session not available.")
        return None, False

    full_response_text = ""
    try:
        print(f"DEBUG: Sending user prompt to chat: '{user_prompt[:50]}...'")
        response_stream = chat_session.send_message(user_prompt, stream=True)
        
        for stream_chunk in response_stream:
            chunk_text_content = ""
            # Robustly extract text from various possible chunk structures
            if hasattr(stream_chunk, 'text'):
                chunk_text_content = stream_chunk.text
            elif hasattr(stream_chunk, 'parts') and stream_chunk.parts and hasattr(stream_chunk.parts[0], 'text'):
                 chunk_text_content = stream_chunk.parts[0].text
            
            if chunk_text_content:
                full_response_text += chunk_text_content
            if message_placeholder:
                message_placeholder.markdown(full_response_text + "▌") # Streaming cursor

            # Check for safety blocking during the stream
            if hasattr(stream_chunk, 'candidates') and stream_chunk.candidates and \
               hasattr(stream_chunk.candidates[0], 'finish_reason') and \
               stream_chunk.candidates[0].finish_reason.name == "SAFETY":
                safety_message = "\n[AI response stopped due to safety reasons.]\n"
                if safety_message not in full_response_text: # Avoid duplicate messages
                    full_response_text += safety_message
                if message_placeholder:
                    message_placeholder.markdown(full_response_text)
                st.warning("AI response was blocked due to safety reasons. Ad not updated.")
                print("WARNING: AI response blocked by safety filter during stream.")
                return full_response_text, False # Return the partial text and False for success

        if message_placeholder:
            message_placeholder.markdown(full_response_text) # Final complete response

        if not full_response_text.strip():
            st.warning("AI returned an empty response. Ad not updated.")
            print("WARNING: AI returned an empty response.")
            return "", False # Empty but not an error, just no content

        # Final check for blocking messages that might not be caught by finish_reason
        # (though finish_reason is the more reliable way)
        is_blocking_message_text = "[content generation stopped due to safety reasons.]" in full_response_text.lower() or \
                                   "[content blocked" in full_response_text.lower()
        if is_blocking_message_text and not (hasattr(stream_chunk, 'candidates') and stream_chunk.candidates and stream_chunk.candidates[0].finish_reason.name == "SAFETY"):
            # This catches cases where the text indicates blocking but finish_reason didn't explicitly state it.
            st.warning("AI response may have been blocked or contain safety messages. Ad not updated.")
            print("WARNING: AI response text indicates potential blocking.")
            return full_response_text, False

        print("DEBUG: Received successful response from chat.")
        return full_response_text, True

    except TypeError as te: # Often related to unexpected stream chunk format
        error_msg = f"Error processing AI response stream (TypeError): {te}"
        st.error(error_msg)
        print(f"ERROR: {error_msg}")
        if message_placeholder: message_placeholder.error(error_msg)
        return None, False
    except Exception as e: # Catch other errors, including potential 401 if token expires mid-chat
        error_msg = f"Error during chat interaction: {e}"
        st.error(error_msg)
        print(f"ERROR: {error_msg}")
        if message_placeholder: message_placeholder.error(f"An error occurred: {e}")
        return None, False