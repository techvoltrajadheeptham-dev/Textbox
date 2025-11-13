# app.py
import streamlit as st
import datetime
import base64
import io
import json
import os
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="WhatsApp Clone",
    page_icon="💬",
    layout="wide"
)

def load_chat_data():
    """Load chat data from JSON file"""
    try:
        if os.path.exists('chat_data.json'):
            with open('chat_data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat data: {e}")
    return {"messages": [], "contacts": ["Alice", "Bob", "Charlie"]}

def save_chat_data():
    """Save chat data to JSON file"""
    try:
        with open('chat_data.json', 'w') as f:
            json.dump({
                'messages': st.session_state.messages,
                'contacts': st.session_state.contacts
            }, f)
    except Exception as e:
        st.error(f"Error saving chat data: {e}")

# Initialize session state
def init_session_state():
    if "initialized" not in st.session_state:
        data = load_chat_data()
        st.session_state.messages = data.get("messages", [])
        st.session_state.contacts = data.get("contacts", ["Alice", "Bob", "Charlie"])
        st.session_state.current_contact = None
        st.session_state.initialized = True

init_session_state()

# Custom CSS for WhatsApp-like styling
st.markdown("""
<style>
    .main {
        background-color: #e5ddd5;
    }
    .sidebar .sidebar-content {
        background-color: #2a2f32;
        color: white;
    }
    .stButton button {
        width: 100%;
        background-color: #2a2f32;
        color: white;
        border: 1px solid #444;
    }
    .stButton button:hover {
        background-color: #3a3f42;
        color: white;
        border: 1px solid #555;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .chat-message.user {
        background-color: #dcf8c6;
        margin-left: 20%;
    }
    .chat-message.contact {
        background-color: white;
        margin-right: 20%;
    }
    .message-time {
        font-size: 0.7rem;
        color: #667781;
        text-align: right;
        margin-top: 0.25rem;
    }
    .message-sender {
        font-weight: bold;
        margin-bottom: 0.25rem;
        color: #128c7e;
    }
</style>
""", unsafe_allow_html=True)

def display_message(message):
    """Display a single message in the chat"""
    if message["type"] == "text":
        st.markdown(f"""
        <div class="chat-message {'user' if message['sender'] == 'You' else 'contact'}">
            <div style="flex-grow: 1;">
                <div class="message-sender">{message['sender']}</div>
                <div>{message['content']}</div>
                <div class="message-time">{message['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif message["type"] == "image":
        st.markdown(f"""
        <div class="chat-message {'user' if message['sender'] == 'You' else 'contact'}">
            <div style="flex-grow: 1;">
                <div class="message-sender">{message['sender']}</div>
                <img src="{message['content']}" style="max-width: 300px; border-radius: 0.5rem;">
                <div class="message-time">{message['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def add_text_message(content, sender, contact):
    """Add a text message to chat"""
    new_message = {
        "type": "text",
        "sender": sender,
        "content": content,
        "time": datetime.datetime.now().strftime("%H:%M"),
        "contact": contact,
        "timestamp": datetime.datetime.now().isoformat()
    }
    st.session_state.messages.append(new_message)
    save_chat_data()

def add_image_message(image_data, sender, contact):
    """Add an image message to chat"""
    new_message = {
        "type": "image",
        "sender": sender,
        "content": image_data,
        "time": datetime.datetime.now().strftime("%H:%M"),
        "contact": contact,
        "timestamp": datetime.datetime.now().isoformat()
    }
    st.session_state.messages.append(new_message)
    save_chat_data()

def main():
    st.title("💬 WhatsApp Clone")
    
    # Sidebar for contacts
    with st.sidebar:
        st.header("📱 Contacts")
        
        # Contact list
        for contact in st.session_state.contacts:
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(f"💬 {contact}", key=f"btn_{contact}"):
                    st.session_state.current_contact = contact
                    st.rerun()
        
        st.markdown("---")
        
        # Add new contact
        st.subheader("Add New Contact")
        new_contact = st.text_input("Contact name:")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Add Contact") and new_contact:
                if new_contact and new_contact not in st.session_state.contacts:
                    st.session_state.contacts.append(new_contact)
                    save_chat_data()
                    st.rerun()
        with col2:
            if st.button("Clear All"):
                st.session_state.messages = []
                st.session_state.contacts = ["Alice", "Bob", "Charlie"]
                save_chat_data()
                st.rerun()
    
    # Main chat area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.current_contact:
            st.header(f"💬 Chat with {st.session_state.current_contact}")
            
            # Display chat messages for current contact
            chat_container = st.container()
            with chat_container:
                contact_messages = [
                    m for m in st.session_state.messages 
                    if m["contact"] == st.session_state.current_contact
                ]
                
                # Sort messages by timestamp
                contact_messages.sort(key=lambda x: x.get("timestamp", ""))
                
                for message in contact_messages:
                    display_message(message)
            
            # Input area
            st.markdown("---")
            
            # Text input
            text_input = st.chat_input(f"Type a message to {st.session_state.current_contact}...")
            
            if text_input:
                add_text_message(text_input, "You", st.session_state.current_contact)
                st.rerun()
            
            # Image upload
            st.subheader("📷 Share Image")
            uploaded_file = st.file_uploader(
                "Choose an image", 
                type=['png', 'jpg', 'jpeg'],
                key="image_uploader"
            )
            
            if uploaded_file is not None:
                # Convert uploaded file to base64 for display
                image = Image.open(uploaded_file)
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                image_data = f"data:image/png;base64,{img_str}"
                
                add_image_message(image_data, "You", st.session_state.current_contact)
                st.rerun()
        
        else:
            st.info("👈 Select a contact from the sidebar to start chatting!")
            st.image("https://via.placeholder.com/400x200/128C7E/FFFFFF?text=Welcome+to+WhatsApp+Clone", 
                    use_column_width=True)
    
    with col2:
        st.header("ℹ️ Chat Info")
        if st.session_state.current_contact:
            contact_message_count = len([
                m for m in st.session_state.messages 
                if m["contact"] == st.session_state.current_contact
            ])
            
            st.success(f"**Active Chat:** {st.session_state.current_contact}")
            st.info(f"**Total Messages:** {contact_message_count}")
            
            if st.button("🗑️ Clear This Chat", type="secondary"):
                st.session_state.messages = [
                    m for m in st.session_state.messages 
                    if m["contact"] != st.session_state.current_contact
                ]
                save_chat_data()
                st.rerun()

if __name__ == "__main__":
    main()