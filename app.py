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

def initialize_app():
    """Initialize all session state variables"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.session_state.uploaded_files = {}
        
        # Load or initialize data
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'users' not in st.session_state:
            st.session_state.users = {}
        if 'contacts' not in st.session_state:
            st.session_state.contacts = {}

def save_data():
    """Save all data to session state (for deployment compatibility)"""
    # In deployed version, data persists in session state during the session
    pass

def login_section():
    """User login/registration"""
    st.sidebar.header("🔐 Login / Register")
    
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login", key="login_btn", use_container_width=True):
            if username and password:
                if username in st.session_state.users:
                    st.session_state.current_user = username
                    st.rerun()
                else:
                    st.error("User not found! Please register first.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username")
        new_password = st.text_input("Choose Password", type="password", key="register_password")
        if st.button("Register", key="register_btn", use_container_width=True):
            if new_username and new_password:
                if new_username not in st.session_state.users:
                    st.session_state.users[new_username] = {
                        "password": new_password,
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    st.session_state.contacts[new_username] = []
                    st.session_state.current_user = new_username
                    st.success(f"Welcome {new_username}! You can now add contacts.")
                    st.rerun()
                else:
                    st.error("Username already exists!")

def contacts_section():
    """Manage contacts"""
    st.sidebar.header("👥 Contacts")
    
    # Add contact section
    st.sidebar.subheader("Add Contact")
    new_contact = st.sidebar.text_input("Enter username:")
    if st.sidebar.button("Add Contact", use_container_width=True):
        if new_contact and new_contact != st.session_state.current_user:
            if new_contact in st.session_state.users:
                if new_contact not in st.session_state.contacts[st.session_state.current_user]:
                    st.session_state.contacts[st.session_state.current_user].append(new_contact)
                    st.sidebar.success(f"Added {new_contact}!")
                    st.rerun()
                else:
                    st.sidebar.error("Already in contacts!")
            else:
                st.sidebar.error("User not found!")
    
    st.sidebar.markdown("---")
    
    # Display contacts
    st.sidebar.subheader("Your Contacts")
    user_contacts = st.session_state.contacts.get(st.session_state.current_user, [])
    
    if not user_contacts:
        st.sidebar.info("No contacts yet. Add someone to chat!")
    else:
        for contact in user_contacts:
            if st.sidebar.button(
                f"💬 {contact}", 
                key=f"chat_{contact}",
                use_container_width=True
            ):
                st.session_state.current_contact = contact
                st.rerun()

def display_message(message):
    """Display a chat message"""
    is_current_user = message["sender"] == st.session_state.current_user
    
    if message["type"] == "text":
        st.markdown(f"""
        <div style='
            background-color: {"#dcf8c6" if is_current_user else "white"};
            padding: 12px;
            border-radius: 8px;
            margin: 8px {"20% 0 0 0" if is_current_user else "0 20% 0 0"};
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        '>
            <div style='font-weight: bold; color: #128c7e; margin-bottom: 4px;'>
                {"You" if is_current_user else message["sender"]}
            </div>
            <div style='margin-bottom: 4px;'>{message["content"]}</div>
            <div style='font-size: 0.8em; color: #667781; text-align: right;'>
                {message["time"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif message["type"] == "image":
        st.markdown(f"""
        <div style='
            background-color: {"#dcf8c6" if is_current_user else "white"};
            padding: 12px;
            border-radius: 8px;
            margin: 8px {"20% 0 0 0" if is_current_user else "0 20% 0 0"};
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        '>
            <div style='font-weight: bold; color: #128c7e; margin-bottom: 4px;'>
                {"You" if is_current_user else message["sender"]}
            </div>
            <img src="{message['content']}" style="max-width: 300px; border-radius: 6px; margin-bottom: 4px;">
            <div style='font-size: 0.8em; color: #667781; text-align: right;'>
                {message["time"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

def chat_section():
    """Main chat interface"""
    if not st.session_state.current_contact:
        st.info("👈 Select a contact from the sidebar to start chatting!")
        return
    
    st.header(f"💬 Chat with {st.session_state.current_contact}")
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        # Get messages between current user and contact
        chat_messages = [
            msg for msg in st.session_state.messages
            if (msg["sender"] == st.session_state.current_user and msg["receiver"] == st.session_state.current_contact) or
               (msg["sender"] == st.session_state.current_contact and msg["receiver"] == st.session_state.current_user)
        ]
        
        # Sort by timestamp
        chat_messages.sort(key=lambda x: x["timestamp"])
        
        for message in chat_messages:
            display_message(message)
    
    st.markdown("---")
    
    # Text input
    text_input = st.chat_input(f"Message {st.session_state.current_contact}...")
    if text_input:
        new_message = {
            "type": "text",
            "sender": st.session_state.current_user,
            "receiver": st.session_state.current_contact,
            "content": text_input,
            "time": datetime.datetime.now().strftime("%H:%M"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        st.session_state.messages.append(new_message)
        st.rerun()
    
    # Image upload
    st.subheader("📷 Share Image")
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        key=f"upload_{st.session_state.current_contact}"
    )
    
    if uploaded_file is not None:
        # Check if this is a new upload
        file_key = f"{uploaded_file.name}_{uploaded_file.size}"
        if file_key not in st.session_state.uploaded_files:
            # Process image
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data = f"data:image/png;base64,{img_str}"
            
            # Add image message
            new_message = {
                "type": "image",
                "sender": st.session_state.current_user,
                "receiver": st.session_state.current_contact,
                "content": image_data,
                "time": datetime.datetime.now().strftime("%H:%M"),
                "timestamp": datetime.datetime.now().isoformat()
            }
            st.session_state.messages.append(new_message)
            st.session_state.uploaded_files[file_key] = True
            st.rerun()

def main():
    st.title("💬 WhatsApp Clone")
    
    # Initialize app
    initialize_app()
    
    # Show login if not logged in
    if not st.session_state.current_user:
        login_section()
        st.info("🔐 Please login or register to start chatting")
        return
    
    # Main app interface
    st.sidebar.success(f"Logged in as: **{st.session_state.current_user}**")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.rerun()
    
    contacts_section()
    chat_section()
    
    # Info panel
    with st.sidebar:
        st.markdown("---")
        st.header("ℹ️ App Info")
        st.write(f"**Total Users:** {len(st.session_state.users)}")
        st.write(f"**Your Contacts:** {len(st.session_state.contacts.get(st.session_state.current_user, []))}")
        st.write(f"**Total Messages:** {len(st.session_state.messages)}")
        
        if st.session_state.current_contact:
            chat_count = len([
                msg for msg in st.session_state.messages
                if (msg["sender"] == st.session_state.current_user and msg["receiver"] == st.session_state.current_contact) or
                   (msg["sender"] == st.session_state.current_contact and msg["receiver"] == st.session_state.current_user)
            ])
            st.info(f"**Messages with {st.session_state.current_contact}:** {chat_count}")

if __name__ == "__main__":
    main()
