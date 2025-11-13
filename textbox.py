# whatsapp_fixed.py
import streamlit as st
import datetime
import base64
import io
import json
import os
from PIL import Image

# Page configuration
st.set_page_config(
    page_title="Textbox Clone",
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
    return {"messages": [], "users": {}}

def save_chat_data():
    """Save chat data to JSON file"""
    try:
        with open('chat_data.json', 'w') as f:
            json.dump({
                'messages': st.session_state.messages,
                'users': st.session_state.users
            }, f)
    except Exception as e:
        st.error(f"Error saving chat data: {e}")

def init_session_state():
    """Initialize session state with user management"""
    if "initialized" not in st.session_state:
        data = load_chat_data()
        st.session_state.messages = data.get("messages", [])
        st.session_state.users = data.get("users", {})
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.session_state.initialized = True
        st.session_state.uploaded_files = {}  # Track uploaded files

init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #e5ddd5;
    }
    .sidebar .sidebar-content {
        background-color: #2a2f32;
        color: white;
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

def login_section():
    """User login/registration section"""
    st.sidebar.header("🔐 Login / Register")
    
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        if st.button("Login", key="login_btn"):
            if username and username in st.session_state.users:
                st.session_state.current_user = username
                st.rerun()
            else:
                st.error("User not found! Please register first.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username")
        if st.button("Register", key="register_btn"):
            if new_username:
                if new_username not in st.session_state.users:
                    st.session_state.users[new_username] = {
                        "created_at": datetime.datetime.now().isoformat(),
                        "contacts": []
                    }
                    st.session_state.current_user = new_username
                    save_chat_data()
                    st.rerun()
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please enter a username")

def display_message(message):
    """Display a single message in the chat"""
    sender_display = "You" if message["sender"] == st.session_state.current_user else message["sender"]
    
    if message["type"] == "text":
        st.markdown(f"""
        <div class="chat-message {'user' if message['sender'] == st.session_state.current_user else 'contact'}">
            <div style="flex-grow: 1;">
                <div class="message-sender">{sender_display}</div>
                <div>{message['content']}</div>
                <div class="message-time">{message['time']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif message["type"] == "image":
        st.markdown(f"""
        <div class="chat-message {'user' if message['sender'] == st.session_state.current_user else 'contact'}">
            <div style="flex-grow: 1;">
                <div class="message-sender">{sender_display}</div>
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
    """Add an image message to chat - FIXED to prevent duplicates"""
    # Check if this image was already sent in the last 2 seconds
    recent_messages = [
        msg for msg in st.session_state.messages[-5:] 
        if msg.get("sender") == sender and msg.get("contact") == contact
    ]
    
    for msg in recent_messages:
        if msg.get("content") == image_data:
            # This image was already sent recently
            return
    
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

def contacts_section():
    """Contacts management section"""
    st.sidebar.header("👥 Contacts")
    
    # Add contact
    new_contact = st.sidebar.text_input("Add contact by username:")
    if st.sidebar.button("Add Contact") and new_contact:
        if new_contact in st.session_state.users:
            if new_contact not in st.session_state.users[st.session_state.current_user]["contacts"]:
                st.session_state.users[st.session_state.current_user]["contacts"].append(new_contact)
                save_chat_data()
                st.sidebar.success(f"Added {new_contact} to contacts!")
                st.rerun()
            else:
                st.sidebar.error("Contact already added!")
        else:
            st.sidebar.error("User not found!")
    
    st.sidebar.markdown("---")
    
    # Display contacts
    current_user_contacts = st.session_state.users[st.session_state.current_user].get("contacts", [])
    
    if not current_user_contacts:
        st.sidebar.info("No contacts yet. Add someone to start chatting!")
    else:
        st.sidebar.subheader("Your Contacts:")
        for contact in current_user_contacts:
            if st.sidebar.button(f"💬 {contact}", key=f"chat_{contact}"):
                st.session_state.current_contact = contact
                st.rerun()

def chat_section():
    """Main chat section"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.session_state.current_contact:
            st.header(f"💬 Chat with {st.session_state.current_contact}")
            
            # Display messages for this chat
            chat_container = st.container()
            with chat_container:
                # Get messages between current user and current contact
                chat_messages = [
                    m for m in st.session_state.messages 
                    if ((m["sender"] == st.session_state.current_user and m["contact"] == st.session_state.current_contact) or
                        (m["sender"] == st.session_state.current_contact and m["contact"] == st.session_state.current_user))
                ]
                
                # Sort by timestamp
                chat_messages.sort(key=lambda x: x.get("timestamp", ""))
                
                for message in chat_messages:
                    display_message(message)
            
            # Input area
            st.markdown("---")
            
            # Text input
            text_input = st.chat_input(f"Type a message to {st.session_state.current_contact}...")
            
            if text_input:
                add_text_message(text_input, st.session_state.current_user, st.session_state.current_contact)
                st.rerun()
            
            # Image upload - FIXED to prevent multiple sends
            st.subheader("📷 Share Image")
            
            # Use a unique key based on current contact to prevent re-upload issues
            upload_key = f"image_upload_{st.session_state.current_contact}"
            
            uploaded_file = st.file_uploader(
                "Choose an image", 
                type=['png', 'jpg', 'jpeg'],
                key=upload_key
            )
            
            if uploaded_file is not None:
                # Check if this is a new file upload
                file_id = f"{st.session_state.current_user}_{st.session_state.current_contact}_{uploaded_file.name}"
                
                if file_id not in st.session_state.uploaded_files:
                    # Convert uploaded file to base64
                    image = Image.open(uploaded_file)
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    image_data = f"data:image/png;base64,{img_str}"
                    
                    add_image_message(image_data, st.session_state.current_user, st.session_state.current_contact)
                    st.session_state.uploaded_files[file_id] = True
                    st.rerun()
        
        else:
            st.info("👈 Select a contact to start chatting!")
    
    with col2:
        st.header("ℹ️ Chat Info")
        if st.session_state.current_contact:
            # Count messages in this chat
            chat_message_count = len([
                m for m in st.session_state.messages 
                if ((m["sender"] == st.session_state.current_user and m["contact"] == st.session_state.current_contact) or
                    (m["sender"] == st.session_state.current_contact and m["contact"] == st.session_state.current_user))
            ])
            
            st.success(f"**Chat with:** {st.session_state.current_contact}")
            st.info(f"**Messages:** {chat_message_count}")
            
            if st.button("Clear Chat History", type="secondary"):
                # Remove messages from this chat
                st.session_state.messages = [
                    m for m in st.session_state.messages 
                    if not ((m["sender"] == st.session_state.current_user and m["contact"] == st.session_state.current_contact) or
                           (m["sender"] == st.session_state.current_contact and m["contact"] == st.session_state.current_user))
                ]
                save_chat_data()
                st.rerun()

def main():
    st.title("💬 WhatsApp Clone - Multi User")
    
    if not st.session_state.current_user:
        login_section()
        st.info("🔐 Please login or register to start chatting")
    else:
        st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.current_user = None
            st.session_state.current_contact = None
            st.rerun()
        
        contacts_section()
        chat_section()

if __name__ == "__main__":
    main()