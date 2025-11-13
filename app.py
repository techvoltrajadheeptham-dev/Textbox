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

# Database file path
DB_FILE = "chat_database.json"

def load_database():
    """Load the shared database from file"""
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading database: {e}")
    
    # Return empty database structure
    return {
        "users": {},
        "messages": [],
        "contacts": {}
    }

def save_database(data):
    """Save the shared database to file"""
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
        return True
    except Exception as e:
        st.error(f"Error saving database: {e}")
        return False

def initialize_session():
    """Initialize user session"""
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
        st.session_state.current_contact = None
        st.session_state.uploaded_files = {}

def login_section():
    """User login/registration"""
    st.sidebar.header("🔐 Login / Register")
    
    # Load current database
    db = load_database()
    
    tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
    
    with tab1:
        username = st.text_input("Username", key="login_username").strip()
        if st.button("Login", key="login_btn", use_container_width=True):
            if username:
                if username in db['users']:
                    st.session_state.current_user = username
                    # Initialize user contacts if not exists
                    if username not in db['contacts']:
                        db['contacts'][username] = []
                        save_database(db)
                    st.rerun()
                else:
                    st.error("User not found! Please register first.")
    
    with tab2:
        new_username = st.text_input("Choose Username", key="register_username").strip()
        if st.button("Register", key="register_btn", use_container_width=True):
            if new_username:
                if new_username not in db['users']:
                    # Register new user
                    db['users'][new_username] = {
                        "created_at": datetime.datetime.now().isoformat(),
                        "last_login": datetime.datetime.now().isoformat()
                    }
                    # Initialize contacts list for new user
                    db['contacts'][new_username] = []
                    
                    # Save to database
                    if save_database(db):
                        st.session_state.current_user = new_username
                        st.success(f"🎉 Welcome {new_username}! You can now add contacts.")
                        st.rerun()
                    else:
                        st.error("Failed to save user registration.")
                else:
                    st.error("Username already exists!")
            else:
                st.error("Please enter a username")

def contacts_section():
    """Manage contacts"""
    st.sidebar.header("👥 Contacts")
    
    current_user = st.session_state.current_user
    db = load_database()
    
    # Add contact section
    st.sidebar.subheader("Add Contact")
    new_contact = st.sidebar.text_input("Enter username:").strip()
    
    if st.sidebar.button("Add Contact", use_container_width=True, type="primary"):
        if new_contact:
            if new_contact == current_user:
                st.sidebar.error("❌ You cannot add yourself!")
            elif new_contact in db['users']:
                # Add to current user's contacts
                if new_contact not in db['contacts'][current_user]:
                    db['contacts'][current_user].append(new_contact)
                    if save_database(db):
                        st.sidebar.success(f"✅ Added {new_contact} to contacts!")
                        st.rerun()
                    else:
                        st.sidebar.error("❌ Failed to save contact.")
                else:
                    st.sidebar.error("❌ Already in contacts!")
            else:
                st.sidebar.error("❌ User not found! Tell them to register first.")
    
    st.sidebar.markdown("---")
    
    # Display contacts
    st.sidebar.subheader("Your Contacts")
    user_contacts = db['contacts'].get(current_user, [])
    
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
    
    db = load_database()
    
    st.header(f"💬 Chat with {st.session_state.current_contact}")
    
    # Display messages
    chat_container = st.container()
    with chat_container:
        # Get messages between current user and contact
        chat_messages = [
            msg for msg in db['messages']
            if (msg["sender"] == st.session_state.current_user and msg["receiver"] == st.session_state.current_contact) or
               (msg["sender"] == st.session_state.current_contact and msg["receiver"] == st.session_state.current_user)
        ]
        
        # Sort by timestamp
        chat_messages.sort(key=lambda x: x.get("timestamp", ""))
        
        for message in chat_messages:
            display_message(message)
        
        if not chat_messages:
            st.info("No messages yet. Start the conversation!")
    
    st.markdown("---")
    
    # Text input
    text_input = st.chat_input(f"Message {st.session_state.current_contact}...")
    if text_input:
        db = load_database()  # Reload to get latest messages
        new_message = {
            "type": "text",
            "sender": st.session_state.current_user,
            "receiver": st.session_state.current_contact,
            "content": text_input,
            "time": datetime.datetime.now().strftime("%H:%M"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        db['messages'].append(new_message)
        if save_database(db):
            st.rerun()
        else:
            st.error("Failed to send message")
    
    # Image upload
    st.subheader("📷 Share Image")
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=['png', 'jpg', 'jpeg'],
        key=f"upload_{st.session_state.current_contact}"
    )
    
    if uploaded_file is not None:
        # Check if this is a new upload
        file_key = f"{st.session_state.current_user}_{st.session_state.current_contact}_{uploaded_file.name}"
        if file_key not in st.session_state.get('uploaded_files', {}):
            # Process image
            image = Image.open(uploaded_file)
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            image_data = f"data:image/png;base64,{img_str}"
            
            # Add image message
            db = load_database()
            new_message = {
                "type": "image",
                "sender": st.session_state.current_user,
                "receiver": st.session_state.current_contact,
                "content": image_data,
                "time": datetime.datetime.now().strftime("%H:%M"),
                "timestamp": datetime.datetime.now().isoformat()
            }
            db['messages'].append(new_message)
            if save_database(db):
                if 'uploaded_files' not in st.session_state:
                    st.session_state.uploaded_files = {}
                st.session_state.uploaded_files[file_key] = True
                st.rerun()
            else:
                st.error("Failed to send image")

def main():
    st.title("💬 WhatsApp Clone - Shared Database")
    
    # Initialize user session
    initialize_session()
    
    # Show login if not logged in
    if not st.session_state.current_user:
        login_section()
        st.info("🔐 Please login or register to start chatting")
        return
    
    # Main app interface
    db = load_database()
    
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
        st.write(f"**Total Users:** {len(db['users'])}")
        st.write(f"**Your Contacts:** {len(db['contacts'].get(st.session_state.current_user, []))}")
        st.write(f"**Total Messages:** {len(db['messages'])}")
        
        # Show all registered users
        st.markdown("---")
        st.subheader("👤 All Registered Users")
        if db['users']:
            for user in sorted(db['users'].keys()):
                status = "✅ You" if user == st.session_state.current_user else "👤"
                st.write(f"{status} {user}")
        else:
            st.write("No users registered yet")

if __name__ == "__main__":
    main()
