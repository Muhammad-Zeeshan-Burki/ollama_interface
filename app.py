import streamlit as st
import ollama
import json
from typing import List, Dict, Any
import time

st.set_page_config(
    page_title="Shadow Command Interface",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 25%, #2d1b3d 50%, #1a1a1a 75%, #0a0a0a 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        background: rgba(20, 20, 20, 0.95);
        backdrop-filter: blur(15px);
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid rgba(255, 69, 0, 0.6);
        box-shadow: 0 0 25px rgba(255, 69, 0, 0.3), inset 0 0 25px rgba(255, 69, 0, 0.1);
    }
    .creator-badge {
        position: fixed;
        top: 15px;
        right: 20px;
        background: linear-gradient(45deg, #ff4500, #cc3300);
        color: #ffffff;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(255, 69, 0, 0.5);
        z-index: 999;
        text-shadow: 0 0 5px rgba(255, 69, 0, 0.8);
    }
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        text-shadow: 0 0 10px rgba(255, 69, 0, 0.9);
        font-size: 3rem !important;
        margin-bottom: 1rem !important;
        font-weight: bold !important;
    }
    .stSelectbox > div > div {
        background: rgba(25, 25, 25, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        border: 1px solid rgba(255, 69, 0, 0.5);
        box-shadow: 0 0 10px rgba(255, 69, 0, 0.2);
        color: #ffffff;
    }
    .stSelectbox label {
        color: #ff4500 !important;
        font-weight: bold !important;
    }
    .stButton > button {
        background: linear-gradient(45deg, #ff4500, #cc3300, #ff4500);
        color: #ffffff;
        border: none;
        border-radius: 20px;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        box-shadow: 0 0 15px rgba(255, 69, 0, 0.4);
        transition: all 0.3s ease;
        text-shadow: 0 0 5px rgba(255, 69, 0, 0.8);
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: 0 0 25px rgba(255, 69, 0, 0.7);
        background: linear-gradient(45deg, #ff6600, #ff4500, #ff6600);
    }
    .stSidebar {
        background: linear-gradient(180deg, #1a1a1a 0%, #2d1b3d 50%, #1a1a1a 100%);
        border-right: 2px solid rgba(255, 69, 0, 0.6);
    }
    .stChatMessage {
        background: rgba(25, 25, 25, 0.8) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border: 1px solid rgba(255, 69, 0, 0.3) !important;
        margin: 1rem 0 !important;
        box-shadow: 0 0 10px rgba(255, 69, 0, 0.2);
    }
    .stChatMessage p, .stChatMessage div {
        color: #ffffff !important;
    }
    .stChatInput > div > div > textarea {
        background: rgba(25, 25, 25, 0.95) !important;
        color: #ffffff !important;
        border: 2px solid rgba(255, 69, 0, 0.6) !important;
        border-radius: 20px !important;
        font-size: 1rem !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #ff4500 !important;
        box-shadow: 0 0 15px rgba(255, 69, 0, 0.4) !important;
    }
    .stChatInput > div > div > textarea::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    .stError {
        background: rgba(255, 0, 0, 0.15) !important;
        border-left: 4px solid #ff3333 !important;
        color: #ff6666 !important;
    }
    .stSuccess {
        background: rgba(0, 255, 0, 0.15) !important;
        border-left: 4px solid #33ff33 !important;
        color: #66ff66 !important;
    }
    .villain-divider {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #ff4500, transparent);
        margin: 1.5rem 0;
        box-shadow: 0 0 8px rgba(255, 69, 0, 0.5);
    }
    .sidebar-text {
        color: #ffffff !important;
        text-shadow: 0 0 3px rgba(255, 69, 0, 0.4);
    }
    .sidebar-text strong {
        color: #ff4500 !important;
    }
    .stCode {
        background: rgba(25, 25, 25, 0.9) !important;
        border: 1px solid rgba(255, 69, 0, 0.4) !important;
        color: #ff6600 !important;
        border-radius: 6px !important;
    }
</style>
""", unsafe_allow_html=True)

def get_available_models() -> List[str]:
    try:
        models = ollama.list()
        model_names = [model['name'] for model in models['models']]
        return sorted(model_names)
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        st.error("Make sure OLLAMA is running and accessible.")
        return []

def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None

def clear_chat():
    st.session_state.messages = []
    st.rerun()

def stream_response(model: str, messages: List[Dict[str, str]]):
    try:
        ollama_messages = []
        for msg in messages:
            ollama_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        response = ollama.chat(
            model=model,
            messages=ollama_messages,
            stream=True
        )
        
        return response
    except Exception as e:
        st.error(f"Error generating response: {str(e)}")
        return None

def main():
    initialize_session_state()
    
    st.markdown('<div class="creator-badge">⚡ Made by Muhammad Zeeshan Burki</div>', unsafe_allow_html=True)
    
    st.title("🔥 SHADOW COMMAND")
    st.markdown('<hr class="villain-divider">', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown('<div class="sidebar-text"><h3>🎯 Control Hub</h3></div>', unsafe_allow_html=True)
        st.markdown("")
        
        models = get_available_models()
        
        if not models:
            st.error("🚫 No AI models detected!")
            st.markdown('<div class="sidebar-text"><strong>Deploy Models:</strong></div>', unsafe_allow_html=True)
            st.code("ollama pull llama2", language="bash")
            st.stop()
        
        selected_model = st.selectbox(
            "Select AI Asset:",
            options=models,
            index=0 if models else None,
            help="Choose your digital operative"
        )
        
        st.session_state.selected_model = selected_model
        
        if selected_model:
            st.markdown(f'<div class="sidebar-text"><strong>Active Asset:</strong> <code>{selected_model}</code></div>', unsafe_allow_html=True)
        
        st.markdown('<hr class="villain-divider">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Clear", use_container_width=True):
                clear_chat()
        with col2:
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        if st.session_state.messages:
            st.markdown('<hr class="villain-divider">', unsafe_allow_html=True)
            st.markdown('<div class="sidebar-text"><h3>📊 Mission Stats</h3></div>', unsafe_allow_html=True)
            user_msgs = len([m for m in st.session_state.messages if m["role"] == "user"])
            assistant_msgs = len([m for m in st.session_state.messages if m["role"] == "assistant"])
            col1, col2 = st.columns(2)
            with col1:
                st.metric("👤 Operator", user_msgs)
            with col2:
                st.metric("🤖 System", assistant_msgs)
        
        st.markdown('<hr class="villain-divider">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-text"><h3>⚙️ Interface</h3></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-text">🌑 <strong>Shadow Protocol</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-text">⚡ <strong>Command Mode</strong></div>', unsafe_allow_html=True)
    
    # Show chat history first
    if st.session_state.messages:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else:
        # Add some vertical space to center input nicely
        st.markdown("<br>" * 14, unsafe_allow_html=True)
    
    # Chat input at the bottom
    prompt = st.chat_input("💬 Enter your command here...", key="chat_input")
    
    if prompt:
        if not st.session_state.selected_model:
            st.error("🚫 Select an AI asset first!")
            st.stop()
        
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            response_stream = stream_response(
                st.session_state.selected_model,
                st.session_state.messages
            )
            
            if response_stream:
                try:
                    for chunk in response_stream:
                        if 'message' in chunk and 'content' in chunk['message']:
                            full_response += chunk['message']['content']
                            message_placeholder.markdown(full_response + "▌")
                        
                        time.sleep(0.01)
                    
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    error_msg = f"🚨 System Error: {str(e)}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
            else:
                error_msg = "🚨 Communication failure with AI asset."
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    st.markdown('<hr class="villain-divider">', unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align: center; color: #ff6600; font-size: 0.9em; margin-top: 1.5rem; text-shadow: 0 0 5px rgba(255, 102, 0, 0.6);'>
            ⚡ Powered by <strong>OLLAMA</strong> & <strong>Streamlit</strong> | 
            🔥 Shadow Command Interface |
            🎯 Execute with precision
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()