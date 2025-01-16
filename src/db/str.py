import streamlit as st
from chat import main
import os
 
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'sources' not in st.session_state:
    st.session_state.sources = []
 
def create_sidebar():
    with st.sidebar:
        st.markdown("### Analysis Settings")
        st.markdown("---")
        st.markdown("### Document Information")
        st.markdown("**Current Document:** PBM Service Agreement")
        st.markdown("**Last Updated:** December 2024")
        st.markdown("---")
        if st.button("Clear Conversation", type="secondary"):
            st.session_state.chat_history = []
 
def handle_user_input():
    if st.session_state.messages:
        user_input = st.session_state.messages

        with st.spinner("Analyzing contract details..."):
            response, sources = main(user_input)
            st.session_state.messages.append("assistant", response)
            st.session_state.sources = sources
 
 
def main(): 
    # CSS styling
    st.markdown("""
<style>
        .stApp {
            background-color: #f8f9fa;
            color: #212529;
        }
        .css-1d391kg {
            background-color: #ffffff;
        }
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #dee2e6;
        }
        .main-header {
            background-color: #ffffff;
            padding: 1.5rem;
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .message-container {
            margin-bottom: 1.5rem;
            padding: 0.5rem;
        }
        .user-message {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            width: 100%;
        }
        .assistant-message {
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1rem 0;
            width: 100%;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }
        .input-container {
            background-color: #ffffff;
            border-top: 1px solid #dee2e6;
            padding: 1.5rem;
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 100;
            box-shadow: 0 -2px 4px rgba(0,0,0,0.05);
        }
        .stTextInput > div > div > input {
            background-color: #ffffff;
            border: 1px solid #ced4da;
            border-radius: 6px;
            padding: 0.75rem 1rem;
            color: #212529;
            font-size: 1rem;
        }
        .stTextInput > div > div > input:focus {
            border-color: #80bdff;
            box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
        }
        .stButton > button {
            background-color: #0d6efd;
            color: white;
            border: none;
            padding: 0.5rem 2rem;
            font-weight: 500;
            border-radius: 6px;
            transition: background-color 0.2s;
        }
        .stButton > button:hover {
            background-color: #0b5ed7;
        }
        h1, h2, h3 {
            color: #212529 !important;
            font-weight: 600;
        }
        p, span, label {
            color: #495057 !important;
        }
        .stMarkdown {
            color: #212529;
        }
        .chat-container {
            margin-bottom: 100px;
            padding: 0 2rem;
        }
        .welcome-container {
            padding: 2rem;
            text-align: center;
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin: 2rem 0;
        }
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
 
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
</style>
    """, unsafe_allow_html=True)
 
    # Create sidebar
    st.session_state.k_value = create_sidebar()
 
    # Main content container
    main_container = st.container()
 
    with main_container:
        # Header
        st.markdown('<div class="main-header">', unsafe_allow_html=True)
        col1, col2 = st.columns([6,1])
        with col1:
            st.title("PBM Contract Analysis")
            st.markdown("Enterprise Contract Analysis System")
        with col2:
            st.markdown("**Status:** Active")
            st.markdown("**Version:** 2.1.0")
        st.markdown('</div>', unsafe_allow_html=True)
        # Chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.markdown("""
<div class="welcome-container">
<h3>Welcome to PBM Contract Analysis</h3>
<p>This AI-powered system helps you analyze and understand PBM Service Agreements. You can:</p>
<p>• Ask questions about contract terms and definitions</p>
<p>• Query specific clauses and requirements</p>
<p>• Get insights about pricing and rebates</p>
<p>• Understand compliance obligations</p>
<p>Start by typing your question below.</p>
</div>
                """, unsafe_allow_html=True)
            # Display messages with unique source button keys
            for msg_idx, (role, content) in enumerate(st.session_state.chat_history):
                st.markdown('<div class="message-container">', unsafe_allow_html=True)
                message_style = "user-message" if role == "user" else "assistant-message"
                st.markdown(f'<div class="{message_style}">{content}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
 
                # If it's a user question, show source buttons with unique keys
                if role == "user" and 'sources' in st.session_state and st.session_state.sources:
                    for src_idx, source in enumerate(st.session_state.sources):
                        unique_key = f"source_button_{msg_idx}_{src_idx}_{os.path.basename(source).replace(' ', '_')}"
                        try:
                            with open(source, "rb") as source_file:
                                source_data = source_file.read()
                                st.download_button(
                                    label=f"Download Source Document {src_idx + 1}",
                                    data=source_data,
                                    file_name=os.path.basename(source),
                                    mime="application/octet-stream",
                                    key=unique_key
                                )
                        except Exception as e:
                            st.error(f"Error loading source document: {str(e)}")
 
        # Input container
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([6, 1])
        with col1:
            st.text_input(
                "",
                key="user_message",
                placeholder="Ask a question about the PBM contract...",
                on_change=handle_user_input
            )
        with col2:
            st.button("Send", on_click=handle_user_input, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)
 
if __name__ == "__main__":
    main()